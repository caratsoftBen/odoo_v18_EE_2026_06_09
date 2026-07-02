from datetime import datetime, time

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class IgmKpi(models.AbstractModel):
    _name = 'igm.kpi'
    _description = "IGM KPI Provider"

    @api.model
    def _resolve_employee(self, employee):
        if isinstance(employee, models.BaseModel):
            return employee[:1]
        return self.env['hr.employee'].browse(int(employee))

    @api.model
    def _month_bounds(self, ref_date=None):
        ref_date = fields.Date.to_date(ref_date) or fields.Date.context_today(self)
        first = ref_date.replace(day=1)
        last = first + relativedelta(months=1, days=-1)
        start_dt = datetime.combine(first, time.min)
        end_dt = datetime.combine(last, time.max)
        return first, last, start_dt, end_dt

    @api.model
    def employee_max_hours_for_month(self, employee, ref_date=None):
        """Contractual working-hour ceiling for the month of ``ref_date``.

        Uses the contract's ``igm_max_hours_per_month`` when set; otherwise falls
        back to the hours implied by the active working schedule. Returns 0.0 when
        neither is available.
        """
        employee = self._resolve_employee(employee)
        if not employee:
            return 0.0
        first, last, start_dt, end_dt = self._month_bounds(ref_date)
        contracts = employee.sudo()._get_contracts(first, last, states=['open'])
        contract = contracts[:1]
        if contract and contract.igm_max_hours_per_month:
            return contract.igm_max_hours_per_month
        calendar = (contract.resource_calendar_id if contract else False) \
            or employee.resource_calendar_id
        if calendar:
            return calendar.get_work_hours_count(start_dt, end_dt)
        return 0.0

    @api.model
    def employee_worked_hours_for_month(self, employee, ref_date=None):
        """Hours already booked on timesheets for the month of ``ref_date``."""
        employee = self._resolve_employee(employee)
        if not employee:
            return 0.0
        first, last, start_dt, end_dt = self._month_bounds(ref_date)
        lines = self.env['account.analytic.line'].sudo().search([
            ('employee_id', '=', employee.id),
            ('project_id', '!=', False),
            ('date', '>=', first),
            ('date', '<=', last),
        ])
        return sum(lines.mapped('unit_amount'))

    @api.model
    def employee_planned_hours_for_month(self, employee, ref_date=None):
        """Still-outstanding planned hours on open tasks for the month.

        For each open (not closed) task assigned to the employee and scheduled in
        the month, this counts the allocated hours not yet logged by the employee
        on that task, so hours are never double-counted against worked hours.
        """
        employee = self._resolve_employee(employee)
        if not employee or not employee.user_id:
            return 0.0
        first, last, start_dt, end_dt = self._month_bounds(ref_date)
        Task = self.env['project.task'].sudo()
        date_field = 'planned_date_begin' if 'planned_date_begin' in Task._fields else 'date_deadline'
        tasks = Task.search([
            ('user_ids', 'in', employee.user_id.ids),
            ('is_closed', '=', False),
            ('allocated_hours', '>', 0.0),
            (date_field, '>=', start_dt),
            (date_field, '<=', end_dt),
        ])
        planned = 0.0
        for task in tasks:
            logged = sum(task.sudo().timesheet_ids.filtered(
                lambda l: l.employee_id == employee and first <= l.date <= last
            ).mapped('unit_amount'))
            planned += max(task.allocated_hours - logged, 0.0)
        return planned

    @api.model
    def employee_remaining_hours_for_month(self, employee, ref_date=None):
        """Working hours left before the monthly contractual cap is breached.

        remaining = max monthly hours - worked (timesheet) - outstanding planned.
        A negative result means the employee is already over the contractual cap.
        """
        max_hours = self.employee_max_hours_for_month(employee, ref_date)
        worked = self.employee_worked_hours_for_month(employee, ref_date)
        planned = self.employee_planned_hours_for_month(employee, ref_date)
        return max_hours - worked - planned

    @api.model
    def employee_hours_breakdown_for_month(self, employee, ref_date=None):
        """Full breakdown behind :meth:`employee_remaining_hours_for_month`.

        Returns a dict with ``max_hours``, ``worked_hours``, ``planned_hours`` and
        ``remaining_hours`` for consumers that want to render the components.
        """
        max_hours = self.employee_max_hours_for_month(employee, ref_date)
        worked = self.employee_worked_hours_for_month(employee, ref_date)
        planned = self.employee_planned_hours_for_month(employee, ref_date)
        return {
            'max_hours': max_hours,
            'worked_hours': worked,
            'planned_hours': planned,
            'remaining_hours': max_hours - worked - planned,
        }

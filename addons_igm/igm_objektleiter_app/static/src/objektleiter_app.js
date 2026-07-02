/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { KpiBadge } from "@igm_kpis/kpi_badge";

function hhmm(hours) {
    const total = Math.round((hours || 0) * 60);
    return String(Math.floor(total / 60)).padStart(2, "0") + ":" + String(total % 60).padStart(2, "0");
}

function taskTime(startISO, endISO) {
    if (!startISO) {
        return "Ungeplant";
    }
    const t = (d) => d.toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" });
    const start = new Date(startISO);
    return endISO ? `${t(start)}–${t(new Date(endISO))}` : t(start);
}

function dayKey(d) {
    return `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`;
}

export class ObjektleiterApp extends Component {
    static template = "igm_objektleiter_app.ObjektleiterApp";
    static components = { KpiBadge };
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            loading: true,
            error: null,
            sites: [],
            employees: [],
            expanded: {},
            dragEmpId: null,
            modal: null,
            busy: false,
        });
        onWillStart(() => this.load());
    }

    async load() {
        this.state.loading = true;
        this.state.error = null;
        try {
            this.applyDashboard(await this.orm.call("project.task", "igm_api_ol_get_dashboard", []));
        } catch (e) {
            this.state.error = (e && e.message) || String(e);
        } finally {
            this.state.loading = false;
        }
    }

    applyDashboard(data) {
        this.state.sites = data.sites || [];
        this.state.employees = data.employees || [];
    }

    hhmm(h) { return hhmm(h); }
    taskTime(task) { return taskTime(task.plannedStart, task.plannedEnd); }

    siteDays(site) {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const days = [];
        const byKey = {};
        for (let i = 0; i < 7; i++) {
            const d = new Date(today);
            d.setDate(today.getDate() + i);
            const day = {
                key: dayKey(d),
                label: d.toLocaleDateString("de-DE", { weekday: "short", day: "2-digit", month: "2-digit" }),
                isToday: i === 0,
                tasks: [],
            };
            days.push(day);
            byKey[day.key] = day;
        }
        for (const task of site.tasks) {
            if (!task.plannedStart) {
                continue;
            }
            const start = new Date(task.plannedStart);
            const day = byKey[dayKey(start)] || (start < today ? days[0] : days[days.length - 1]);
            day.tasks.push(task);
        }
        return days;
    }

    toggle(siteId) {
        this.state.expanded[siteId] = !this.state.expanded[siteId];
    }

    // --- drag & drop ---------------------------------------------------------
    onDragStart(emp, ev) {
        this.state.dragEmpId = emp.id;
        if (ev.dataTransfer) {
            ev.dataTransfer.effectAllowed = "move";
            ev.dataTransfer.setData("text/plain", String(emp.id));
        }
    }
    onDragEnd() {
        this.state.dragEmpId = null;
    }
    onDragOver(ev) {
        if (this.state.dragEmpId) {
            ev.preventDefault();
            ev.dataTransfer.dropEffect = "move";
        }
    }
    onDrop(task, ev) {
        ev.preventDefault();
        const empId = this.state.dragEmpId;
        this.state.dragEmpId = null;
        if (!empId || task.done) {
            return;
        }
        if (!task.assignees.length) {
            this.assign(task.id, empId);
            return;
        }
        const emp = this.state.employees.find((e) => e.id === empId);
        this.state.modal = {
            taskId: task.id,
            employeeId: empId,
            taskTitle: task.title,
            empName: emp ? emp.name : "",
            isRecurring: task.recurring,
            choice: "substitute_once",
        };
    }

    // --- backend calls -------------------------------------------------------
    async assign(taskId, empId) {
        await this._run(() =>
            this.orm.call("project.task", "igm_api_ol_assign", [[taskId], empId])
        );
    }

    closeModal() {
        if (!this.state.busy) {
            this.state.modal = null;
        }
    }
    stop() {}

    async applyModal() {
        const m = this.state.modal;
        if (!m || !m.choice) {
            return;
        }
        await this._run(() => {
            if (m.choice === "assign_additional") {
                return this.orm.call("project.task", "igm_api_ol_assign", [[m.taskId], m.employeeId]);
            }
            const scope = m.choice === "substitute_series" ? "series" : "once";
            return this.orm.call("project.task", "igm_api_ol_substitute", [[m.taskId], m.employeeId, scope]);
        });
        this.state.modal = null;
    }

    async _run(fn) {
        this.state.busy = true;
        this.state.error = null;
        try {
            const data = await fn();
            if (data) {
                this.applyDashboard(data);
            }
        } catch (e) {
            this.state.error = (e && e.data && e.data.message) || (e && e.message) || String(e);
        } finally {
            this.state.busy = false;
        }
    }
}

registry.category("actions").add("igm_objektleiter_app", ObjektleiterApp);

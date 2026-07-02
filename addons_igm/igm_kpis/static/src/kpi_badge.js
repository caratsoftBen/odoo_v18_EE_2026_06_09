/** @odoo-module **/

import { Component } from "@odoo/owl";

export class KpiBadge extends Component {
    static template = "igm_kpis.KpiBadge";
    static props = {
        kpi: { type: Object, optional: true },
    };

    get pct() {
        const p = (this.props.kpi && this.props.kpi.pct) || 0;
        return Math.max(0, Math.min(1, p));
    }

    get text() {
        const kpi = this.props.kpi || {};
        const v = Math.round((kpi.value || 0) * 10) / 10;
        const s = Number.isInteger(v) ? String(v) : v.toFixed(1).replace(".", ",");
        return s + (kpi.unit || "");
    }
}

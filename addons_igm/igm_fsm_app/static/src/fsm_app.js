/** @odoo-module **/

import { Component, useState, useRef, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

function hhmm(hours) {
    const total = Math.round((hours || 0) * 60);
    return String(Math.floor(total / 60)).padStart(2, "0") + ":" + String(total % 60).padStart(2, "0");
}

function plannedWindow(startISO, endISO) {
    if (!startISO) {
        return "";
    }
    const start = new Date(startISO);
    const day = start.toLocaleDateString("de-DE", { weekday: "long" });
    const t = (d) => d.toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" });
    return endISO ? `${day}, ${t(start)} – ${t(new Date(endISO))}` : `${day}, ${t(start)}`;
}

export class FsmApp extends Component {
    static template = "igm_fsm_app.FsmApp";
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.fileInput = useRef("fileInput");
        this.state = useState({
            loading: true,
            error: null,
            task: null,
            adjustOpen: false,
            reasonOpen: false,
            reason: "",
            overridden: false,
            adjH: 0,
            adjM: 0,
            contactOpen: false,
            fotoOpen: false,
            confirmOpen: false,
            submitting: false,
            completed: false,
            done: false,
        });
        onWillStart(() => this.load());
    }

    async load() {
        this.state.loading = true;
        this.state.error = null;
        try {
            const tasks = await this.orm.call("project.task", "igm_fsm_api_get_my_tasks", []);
            const task = tasks[0] || null;
            this.state.task = task;
            if (task) {
                const total = Math.round((task.allocatedHours || 0) * 60);
                this.state.adjH = Math.floor(total / 60);
                this.state.adjM = total % 60;
            }
        } catch (e) {
            this.state.error = (e && e.message) || String(e);
        } finally {
            this.state.loading = false;
        }
    }

    get loggedHours() {
        const s = this.state;
        return s.overridden ? s.adjH + s.adjM / 60 : (s.task ? s.task.allocatedHours || 0 : 0);
    }
    get loggedTime() { return hhmm(this.loggedHours); }
    get adjLabel() { return String(this.state.adjH).padStart(2, "0") + ":" + String(this.state.adjM).padStart(2, "0"); }
    get planned() { return plannedWindow(this.state.task.plannedStart, this.state.task.plannedEnd); }
    get allocatedLabel() { return hhmm(this.state.task ? this.state.task.allocatedHours || 0 : 0); }

    initials(name) {
        return (name || "").trim().split(/\s+/).slice(0, 2).map((w) => (w[0] || "").toUpperCase()).join("");
    }
    mapsUrl(addr) { return "https://www.google.com/maps/search/?api=1&query=" + encodeURIComponent(addr || ""); }
    wa(phone) { return (phone || "").replace(/\D/g, ""); }
    photoSrc(id) { return "/web/image/" + id + "?width=240&height=240"; }

    get reasonValid() { return !!this.state.reason.trim(); }
    openAdjust() {
        if (this.state.reasonOpen || this.state.adjustOpen) {
            this.state.reasonOpen = false;
            this.state.adjustOpen = false;
        } else {
            this.state.reasonOpen = true;
        }
    }
    confirmReason() {
        if (this.reasonValid) {
            this.state.reasonOpen = false;
            this.state.adjustOpen = true;
        }
    }
    openContact() { this.state.contactOpen = true; }
    closeContact() { this.state.contactOpen = false; }
    openFoto() { this.state.fotoOpen = true; }
    closeFoto() { this.state.fotoOpen = false; }
    openConfirm() { this.state.confirmOpen = true; }
    closeConfirm() { if (!this.state.submitting) { this.state.confirmOpen = false; } }
    finish() { this.state.done = false; }
    stop() {}

    incTime() { this.step(15); }
    decTime() { this.step(-15); }
    step(delta) {
        const s = this.state;
        const total = Math.max(0, Math.min(8 * 60, s.adjH * 60 + s.adjM + delta));
        s.adjH = Math.floor(total / 60);
        s.adjM = total % 60;
        s.overridden = true;
    }
    resetTime() {
        const total = Math.round((this.state.task.allocatedHours || 0) * 60);
        this.state.adjH = Math.floor(total / 60);
        this.state.adjM = total % 60;
        this.state.overridden = false;
    }

    pickPhoto() {
        if (this.fileInput.el) {
            this.fileInput.el.click();
        }
    }
    onFile(ev) {
        const file = ev.target.files && ev.target.files[0];
        ev.target.value = "";
        if (!file) {
            return;
        }
        if (file.size > 20 * 1024 * 1024) {
            this.state.error = "Das Foto ist zu groß (max. 20 MB).";
            return;
        }
        const reader = new FileReader();
        reader.onload = async () => {
            const dataUrl = String(reader.result);
            try {
                const attId = await this.orm.call("project.task", "igm_fsm_api_add_photo", [[this.state.task.id], dataUrl]);
                if (attId) {
                    this.state.task.photos.push(attId);
                    this.state.task.photoCount = this.state.task.photos.length;
                }
            } catch (e) {
                this.state.error = (e && e.message) || String(e);
            }
        };
        reader.readAsDataURL(file);
    }

    async confirmDone() {
        this.state.submitting = true;
        this.state.error = null;
        try {
            const kwargs = this.state.overridden
                ? { worked_hours: this.loggedHours, reason: this.state.reason }
                : {};
            await this.orm.call("project.task", "igm_fsm_api_mark_done", [[this.state.task.id]], kwargs);
            this.state.confirmOpen = false;
            this.state.completed = true;
            this.state.done = true;
        } catch (e) {
            this.state.error = (e && e.message) || String(e);
        } finally {
            this.state.submitting = false;
        }
    }
}

registry.category("actions").add("igm_fsm_app", FsmApp);

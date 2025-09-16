/** @odoo-module **/

import { registry } from "@web/core/registry";
import { AnalyticDistribution } from "@analytic/components/analytic_distribution/analytic_distribution";


export class LocationAnalyticDistribution extends AnalyticDistribution {
    static template = "analytic.AnalyticDistribution";

    setup() {
        super.setup?.();

        const location = this.props.record.data?.location_id;
        console.log("📍 Location (selection related):", location);
    }
    recordProps(line) {
        const analyticAccountFields = {
            id: { type: "int" },
            display_name: { type: "char" },
            color: { type: "int" },
            plan_id: { type: "many2one" },
            root_plan_id: { type: "many2one" },
        };
    
        const recordFields = {};
        const values = {};
        const location = this.props.record.data?.location_id;
    
        line.analyticAccounts.forEach((account) => {
            const fieldName = `x_plan${account.planId}_id`;
            const domain = [["root_plan_id", "=", account.planId]];
            
            if (location) {
                domain.push(["location_id", "=", location]);
            }
    
            recordFields[fieldName] = {
                string: account.planName,
                relation: "account.analytic.account",
                type: "many2one",
                related: {
                    fields: analyticAccountFields,
                    activeFields: analyticAccountFields,
                },
                domain,
            };
    
            values[fieldName] = account?.accountId || false;
        });
    
        recordFields["percentage"] = {
            string: "Percentage",
            type: "percentage",
            cellClass: "numeric_column_width",
            ...this.decimalPrecision,
        };
        values["percentage"] = line.percentage;
    
        if (this.props.amount_field) {
            const { string, name, type, currency_field } = this.props.record.fields[this.props.amount_field];
            recordFields[name] = { string, name, type, currency_field, cellClass: "numeric_column_width" };
            values[name] = this.props.record.data[name] * values["percentage"];
    
            if (currency_field) {
                const { string, name, type, relation } = this.props.record.fields[currency_field];
                recordFields[currency_field] = { name, string, type, relation, invisible: true };
                values[currency_field] = this.props.record.data[currency_field][0];
            }
        }
    
        return {
            fields: recordFields,
            values: values,
            activeFields: recordFields,
            onRecordChanged: async (record, changes) => await this.lineChanged(record, changes, line),
        };
    }
}

// Aquí defino el nombre del widget : 'location_analytic_distribution'
registry.category("fields").add("location_analytic_distribution", {
    component: LocationAnalyticDistribution,
    supportedTypes: ["json"],
    fieldDependencies: [{ name: "analytic_precision", type: "integer" }],
});

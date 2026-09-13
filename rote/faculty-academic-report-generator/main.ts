#!/usr/bin/env -S rote play run
/**
 * @rote-frontmatter
 * ---
 * name: faculty-academic-report-generator
 * description: Generate a concise faculty academic report with performance trends, top performers, attention areas, and recommendations.
 * provenance:
 *   author: syedabegem@gmail.com
 * metadata:
 *   rote_version: 0.82.0
 *   version: 0.0.1
 *   status: draft
 *   kind: atomic
 *   flow_type: parallel
 *   execution_model: steps_with_presentation
 *   requires_endpoints: []
 *   requires_sessions: false
 *   discoverability:
 *     tags:
 *     - academic-performance
 *   hardcode_audit:
 *     schema: 2
 *     suspicion_count: 2
 *     audit_sha256: c71586fe1cf9d4bc2c4f5285485cd295963ac362bcdfd1b1b5d1864bff85d7e4
 *   exploration_model: null
 * parameters:
 * - name: project_dir
 *   param_type: string
 *   required: true
 *   default: null
 *   description: Academic performance project directory
 * - name: python_path
 *   param_type: string
 *   required: true
 *   default: null
 *   description: Python interpreter used by the project
 * - name: csv_path
 *   param_type: string
 *   required: true
 *   default: null
 *   description: Student marks CSV file
 * steps:
 *   generate_report:
 *     type: process.exec
 *     argv:
 *     - bash
 *     - -c
 *     - cd "$1" && "$2" main.py report --csv "$3"
 *     - bash
 *     - $project_dir
 *     - $python_path
 *     - $csv_path
 *     exit:
 *       accepted_codes: [0, 1]
 * presentation_fixtures:
 *   generate_report:
 *     completed: resources/presentation-fixtures/generate_report/completed.yaml
 *     partial_coverage: resources/presentation-fixtures/generate_report/partial.yaml
 * ---
 */

const presentationSdk = await import("__ROTE_PRESENTATION_SDK__").catch((cause) => {
  throw new Error(
    "This is a rote steps presentation program. Run it with `rote play run <name>`.",
    { cause },
  );
});
const { FlowOutput, loadPresentationContext, stepName } = presentationSdk;

const out = new FlowOutput();
const ctx = await loadPresentationContext();
out.setRunStatus(ctx.run.status);

const renderedSteps: Record<string, unknown> = {};

// Takes the step handle (not the name) so every `stepName("...")` at the
// call sites stays a literal that lint can verify against `steps:`.
function renderStep(step: ReturnType<typeof ctx.step>): unknown {
  switch (step.outcome.status) {
    case "completed":
      return step.outcome.output.body;
    case "restored": {
      const source = step.outcome.output.source;
      if (source?.status === "partial") {
        return {
          status: "partial",
          body: step.outcome.output.body,
          diagnostics: source.diagnostics,
          additional_diagnostics: source.additional_diagnostics,
        };
      }
      // A clean restored step completed in an earlier run, so it reads like one.
      return step.outcome.output.body;
    }
    case "partial":
      return {
        status: "partial",
        body: step.outcome.output.output.body,
        diagnostics: step.outcome.output.diagnostics,
      };
    case "skipped":
      return { status: "skipped", reason: step.outcome.output.reason };
    case "failed":
      return { status: "failed", message: step.outcome.output.message };
    case "blocked":
      return {
        status: "blocked",
        reason: step.outcome.output.reason,
        blocked_by: step.outcome.output.blocked_by ?? [],
      };
    default:
      // Unreachable while this body matches the SDK. A play exported before a new
      // outcome status was added lands here instead, so name the remedy.
      throw new Error(
        `unsupported step outcome: ${JSON.stringify(step.outcome)}. ` +
          `Re-export the play to regenerate this switch.`,
      );
  }
}
renderedSteps["generate_report"] = renderStep(ctx.step(stepName("generate_report")));

const headlinePrefix = (() => {
  switch (ctx.run.status) {
    case "succeeded":
      return "";
    case "partial":
      return "INCOMPLETE: ";
    case "failed":
      return "FAILED: ";
  }
})();
out.human(`${headlinePrefix}Rendered ${Object.keys(renderedSteps).length} step(s).`);
out.summary(`${headlinePrefix}Rendered ${Object.keys(renderedSteps).length} step(s).`);
out.result({
  run_id: ctx.run.run_id,
  status: ctx.run.status,
  complete: ctx.run.status === "succeeded",
  steps: renderedSteps,
});

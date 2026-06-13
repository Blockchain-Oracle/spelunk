/**
 * Step-event contract — hand-synced to spelunk_core/events.py.
 *
 * The cockpit switches on `type` to pick a React component (the generative-UI
 * registry). Keep this union identical to the Python source of truth.
 *
 * INTENT (phase-2): define the discriminated union below with real payload
 * fields. Stub shapes only for now.
 */

export type StepEventType =
  | "spl"
  | "results"
  | "classification"
  | "forecast"
  | "narrative"
  | "error";

// TODO(phase-2): full discriminated union with payloads, synced to events.py.
export interface StepEvent {
  type: StepEventType;
}

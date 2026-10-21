// The two example infrastructures the dashboard reports on (made-up names).
export const INFRAS = {
  charlie: { jkbName: "Charlie" },
  delta: { jkbName: "Delta" },
};

export const INFRA_NAMES = Object.keys(INFRAS);

export const JKB_INFRA_NAMES = INFRA_NAMES.map((name) => INFRAS[name].jkbName);

// Demo: no real monitoring server exists, so sensor ids do not link anywhere.
export function prtgSensorLink() {
  return null;
}

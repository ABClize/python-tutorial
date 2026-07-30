export function readPlotTheme() {
  const styles = getComputedStyle(document.documentElement);
  const value = (name) => styles.getPropertyValue(name).trim();

  return {
    primary: value("--tutorial-chart-primary"),
    secondary: value("--tutorial-chart-secondary"),
    tertiary: value("--tutorial-chart-tertiary"),
    danger: value("--tutorial-danger"),
    text: value("--tutorial-chart-text"),
    grid: value("--tutorial-chart-grid"),
    markerBorder: value("--tutorial-chart-marker-border"),
  };
}

export function observePlotTheme(callback) {
  const observer = new MutationObserver(callback);
  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["class"],
  });

  return () => observer.disconnect();
}

import DefaultTheme from "vitepress/theme";
import AsyncioTimeline from "../components/AsyncioTimeline.vue";
import ComplexityChart from "../components/ComplexityChart.vue";
import GeneratorFrame from "../components/GeneratorFrame.vue";
import MemoryGrowthChart from "../components/MemoryGrowthChart.vue";
import MutabilityDiagram from "../components/MutabilityDiagram.vue";
import ThreadLockDiagram from "../components/ThreadLockDiagram.vue";
import TruthinessExplorer from "../components/TruthinessExplorer.vue";
import "./custom.css";

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component("AsyncioTimeline", AsyncioTimeline);
    app.component("ComplexityChart", ComplexityChart);
    app.component("GeneratorFrame", GeneratorFrame);
    app.component("MemoryGrowthChart", MemoryGrowthChart);
    app.component("MutabilityDiagram", MutabilityDiagram);
    app.component("ThreadLockDiagram", ThreadLockDiagram);
    app.component("TruthinessExplorer", TruthinessExplorer);
  },
};

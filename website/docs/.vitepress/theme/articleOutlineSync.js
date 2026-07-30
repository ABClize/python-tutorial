import { getScrollOffset } from "vitepress";

const CUSTOM_ASIDE_QUERY = "(min-width: 1120px) and (max-width: 1279px)";
const INSTALL_KEY = "__pythonTutorialArticleOutlineSync";

function updateActiveLink() {
  if (!window.matchMedia(CUSTOM_ASIDE_QUERY).matches) {
    return;
  }

  const container = document.querySelector(".VPDocAsideOutline");
  const marker = container?.querySelector(".outline-marker");
  const links = [...(container?.querySelectorAll("a.outline-link") ?? [])];

  if (!marker || links.length === 0) {
    return;
  }

  const headings = links
    .map((link) => {
      const href = link.getAttribute("href");
      const id = href?.startsWith("#")
        ? decodeURIComponent(href.slice(1))
        : null;
      const heading = id ? document.getElementById(id) : null;

      return heading
        ? {
            link,
            top: heading.getBoundingClientRect().top + window.scrollY,
          }
        : null;
    })
    .filter(Boolean);

  let activeLink = null;
  const isAtBottom =
    Math.abs(
      window.scrollY + window.innerHeight - document.documentElement.scrollHeight,
    ) < 2;

  if (isAtBottom) {
    activeLink = headings.at(-1)?.link ?? null;
  } else if (window.scrollY > 0) {
    const activeLine = window.scrollY + getScrollOffset() + 4;

    for (const heading of headings) {
      if (heading.top > activeLine) {
        break;
      }
      activeLink = heading.link;
    }
  }

  for (const link of links) {
    link.classList.toggle("active", link === activeLink);
  }

  if (activeLink) {
    marker.style.top = `${activeLink.offsetTop + 39}px`;
    marker.style.opacity = "1";
  } else {
    marker.style.top = "33px";
    marker.style.opacity = "0";
  }
}

export function installArticleOutlineSync(router) {
  window[INSTALL_KEY]?.();

  let frameId = 0;
  let isReady = false;

  function scheduleUpdate() {
    if (!isReady || frameId !== 0) {
      return;
    }

    frameId = window.requestAnimationFrame(() => {
      frameId = 0;
      updateActiveLink();
    });
  }

  function handleLoad() {
    isReady = true;
    scheduleUpdate();
  }

  const previousRouteChange = router.onAfterRouteChange;
  const handleRouteChange = async (to) => {
    await previousRouteChange?.(to);
    scheduleUpdate();
  };

  router.onAfterRouteChange = handleRouteChange;
  window.addEventListener("scroll", scheduleUpdate, { passive: true });
  window.addEventListener("resize", scheduleUpdate);

  if (document.readyState === "complete") {
    window.setTimeout(handleLoad, 0);
  } else {
    window.addEventListener("load", handleLoad, { once: true });
  }

  window[INSTALL_KEY] = () => {
    window.removeEventListener("load", handleLoad);
    window.removeEventListener("scroll", scheduleUpdate);
    window.removeEventListener("resize", scheduleUpdate);

    if (frameId !== 0) {
      window.cancelAnimationFrame(frameId);
    }

    if (router.onAfterRouteChange === handleRouteChange) {
      router.onAfterRouteChange = previousRouteChange;
    }
  };
}

import { defineContentScript } from 'wxt/sandbox';
import { settingsItem } from '@/lib/settings';
import { createHider } from '@/lib/hider';
import '@/assets/hider.css';

/**
 * ISOLATED-world content script — the primary layer.
 *
 * Runs at document_start so the hide stylesheet is in place before the page
 * paints (no flash-of-unhidden-content). It also hands the current config to the
 * MAIN-world scriptlet via a CustomEvent, since MAIN-world code cannot read
 * extension storage directly.
 */
export default defineContentScript({
  matches: ['<all_urls>'],
  runAt: 'document_start',
  allFrames: true,
  // 'manifest' injects assets/hider.css through the manifest, i.e. at
  // document_start with no detectable <link> element appended at runtime.
  cssInjectionMode: 'manifest',
  async main() {
    const settings = await settingsItem.getValue();

    // Tell the MAIN-world scriptlet whether to spoof anti-adblock bait.
    window.dispatchEvent(
      new CustomEvent('sch:config', {
        detail: { spoofAntiAdblock: settings.spoofAntiAdblock },
      }),
    );

    if (!settings.enabled) return;

    const hider = createHider(settings);
    hider.injectStyles();
    hider.startObserver();

    // React live when the popup saves new settings.
    settingsItem.watch((next) => hider.update(next));
  },
});

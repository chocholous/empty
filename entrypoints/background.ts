import { defineBackground } from 'wxt/sandbox';
import { browser } from 'wxt/browser';
import { settingsItem } from '@/lib/settings';

/**
 * The MV3 service worker. Kept intentionally thin: cosmetic filtering happens in
 * the content scripts. This just seeds default settings on install so the first
 * page load already has something to work with.
 */
export default defineBackground(() => {
  browser.runtime.onInstalled.addListener(async () => {
    // getValue() returns the fallback when nothing is stored; writing it back
    // materializes the defaults into storage.sync.
    const current = await settingsItem.getValue();
    await settingsItem.setValue(current);
  });
});

import { settingsItem, type HiderSettings } from '@/lib/settings';

const $ = <T extends HTMLElement>(id: string): T => {
  const el = document.getElementById(id);
  if (!el) throw new Error(`Missing element #${id}`);
  return el as T;
};

const enabled = $<HTMLInputElement>('enabled');
const hideSelectors = $<HTMLTextAreaElement>('hideSelectors');
const removeSelectors = $<HTMLTextAreaElement>('removeSelectors');
const spoofAntiAdblock = $<HTMLInputElement>('spoofAntiAdblock');
const status = $<HTMLSpanElement>('status');

/** One selector per line; trims blanks. */
const linesToList = (text: string): string[] =>
  text
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => line.length > 0);

async function load(): Promise<void> {
  const s = await settingsItem.getValue();
  enabled.checked = s.enabled;
  hideSelectors.value = s.hideSelectors.join('\n');
  removeSelectors.value = s.removeSelectors.join('\n');
  spoofAntiAdblock.checked = s.spoofAntiAdblock;
}

async function save(): Promise<void> {
  const next: HiderSettings = {
    enabled: enabled.checked,
    hideSelectors: linesToList(hideSelectors.value),
    removeSelectors: linesToList(removeSelectors.value),
    spoofAntiAdblock: spoofAntiAdblock.checked,
  };
  await settingsItem.setValue(next);
  status.textContent = 'Saved';
  setTimeout(() => (status.textContent = ''), 1500);
}

$('save').addEventListener('click', () => void save());
void load();

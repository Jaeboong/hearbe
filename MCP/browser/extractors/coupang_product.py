"""
Coupang product detail dynamic extraction helpers.
"""

from __future__ import annotations

from typing import Dict, Any


def _build_option_script() -> str:
    return r"""
    () => {
      const options = {};
      const getText = (el) => (el && (el.innerText || el.textContent) || '').trim();
      const hasAny = (text, keywords) => keywords.some((kw) => text.includes(kw));
      const isSelected = (el) => {
        if (!el) return false;
        const cls = (el.className || '').toString();
        if (el.getAttribute && el.getAttribute('aria-selected') === 'true') return true;
        return (
          cls.includes('active') ||
          cls.includes('selected') ||
          cls.includes('is-selected') ||
          cls.includes('twc-border-[#346aff]') ||
          cls.includes('twc-border-[2px]')
        );
      };
      const pickFromSelect = (root) => {
        const select = root.querySelector('select');
        if (!select || select.selectedIndex < 0) return '';
        return getText(select.options[select.selectedIndex]);
      };
      const pickFromCustomSelect = (root) => {
        const custom = root.querySelector('.option-picker-select, .fashion-option-select, [class*="option-select"]');
        if (!custom) return '';
        const label = custom.querySelector('span[class*="flex-1"], span[class*="value"], span');
        return getText(label);
      };
      const pickFromSelectedItems = (root) => {
        const items = root.querySelectorAll(
          'li, button, div[class*="item"], span[class*="item"], div[class*="option"], div[class*="Option"]'
        );
        for (const item of items) {
          if (!isSelected(item)) continue;
          const label = getText(item);
          if (label) return label;
          const img = item.querySelector('img');
          if (img && img.alt) return img.alt.trim();
        }
        return '';
      };

      const pickFromOptionTable = (root) => {
        const selected = root.querySelector('.option-table-list__option--selected');
        if (!selected) return '';
        const name = selected.querySelector('.option-table-list__option-name');
        const text = getText(name) || getText(selected);
        return text;
      };
      const keywords = {
        size: ['사이즈', 'size', '크기'],
        color: ['색상', 'color', '컬러'],
        capacity: ['용량', 'capacity'],
        quantity: ['수량', 'quantity', '개수']
      };
      const sections = document.querySelectorAll('section, div[class*="option"], div[class*="Option"]');
      for (const section of sections) {
        const sectionText = getText(section).toLowerCase();
        if (hasAny(sectionText, keywords.size)) {
          options.size = options.size || pickFromOptionTable(section) || pickFromSelect(section) || pickFromCustomSelect(section) || pickFromSelectedItems(section);
        }
        if (hasAny(sectionText, keywords.color)) {
          const label = section.querySelector('[class*="label-item-text"], [class*="label"] span');
          options.color = options.color || getText(label) || pickFromSelectedItems(section);
        }
        if (hasAny(sectionText, keywords.capacity)) {
          options.capacity = options.capacity || pickFromOptionTable(section) || pickFromSelect(section) || pickFromCustomSelect(section) || pickFromSelectedItems(section);
        }
        if (hasAny(sectionText, keywords.quantity)) {
          const input = section.querySelector('input[type="number"], input[type="text"]');
          if (input && input.value) {
            options.quantity = input.value.trim();
          } else {
            options.quantity = options.quantity || pickFromOptionTable(section) || pickFromSelectedItems(section);
          }
        }
      }
      if (!options.size && !options.color && !options.capacity && !options.option) {
        const fallback = document.querySelector('select[class*="option"], .option-picker-select');
        if (fallback) {
          const label = pickFromSelect(fallback) || getText(fallback);
          if (label) options.option = label;
        }
      }
      return options;
    }
    """


async def extract_coupang_product_options(page) -> Dict[str, Any]:
    """
    Extract selected option values from Coupang product pages.

    Keyword-based scan:
    - size, color, capacity, quantity
    - handles select, custom dropdown, and selected buttons
    """
    try:
        script = _build_option_script()
        return await page.evaluate(script)
    except Exception:
        return {}

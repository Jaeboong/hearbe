"""
Coupang cart dynamic extraction.
"""

from __future__ import annotations

from typing import Dict, Any


async def extract_coupang_cart(page) -> Dict[str, Any]:
    script = r"""
    () => {
      const items = [];
      const getText = (el) => (el && (el.innerText || el.textContent) || '').trim();
      const parsePrice = (text) => {
        if (!text) return '';
        const match = text.match(/\d{1,3}(?:,\d{3})+/);
        if (match) return match[0] + '원';
        return '';
      };
      const pickPriceFrom = (root) => {
        const priceEl = root.querySelector('[data-id="sale-price-ccid"], .price, .twc-text-[20px]');
        if (!priceEl) return '';
        return parsePrice(getText(priceEl));
      };
      const pickArrival = (root) => {
        const parts = [];
        const txt = root.querySelector('#arrive-date-txt');
        const day = root.querySelector('#arrive-date-day');
        const date = root.querySelector('#arrive-date-date');
        const time = root.querySelector('#arrive-date-time');
        const promise = root.querySelector('#promise-txt');
        if (txt) parts.push(getText(txt));
        if (day) parts.push(getText(day));
        if (date) parts.push(getText(date));
        if (time) parts.push(getText(time));
        if (promise) parts.push(getText(promise));
        return parts.join(' ').trim();
      };
      let bundles = document.querySelectorAll('#mainContent [id^="item_"]');
      if (!bundles || bundles.length === 0) {
        bundles = document.querySelectorAll('[id^="item_"]');
      }
      for (const item of bundles) {
        const checkbox = item.querySelector('input[type="checkbox"]');
        if (!checkbox) continue;

        const nameEl = item.querySelector('a span.twc-text-custom-black')
          || item.querySelector('#name span.twc-text-custom-black')
          || item.querySelector('#name span');
        let name = getText(nameEl);
        if (!name) {
          name = (checkbox.getAttribute('title') || '').trim();
        }

        const optionEl = item.querySelector('span.twc-text-custom-637381')
          || item.querySelector('#name span.twc-text-custom-637381');
        let option = getText(optionEl);
        if (option) {
          option = option.replace('옵션', '').replace(':', '').trim();
        }

        const price = pickPriceFrom(item);
        const arrival = pickArrival(item);
        const qtyInput = item.querySelector('input.cart-quantity-input');
        const quantity = qtyInput ? qtyInput.value : '';
        const selectedAttr = item.getAttribute('data-selected');
        const selected = (selectedAttr === 'true') || (checkbox ? checkbox.checked === true : false);

        if (name) {
          items.push({
            name,
            option,
            arrival,
            price,
            quantity,
            selected,
          });
        }
      }

      const summary = {};
      const totalArea = document.querySelector('[data-component-id="total-price"]');
      if (totalArea) {
        const rows = totalArea.querySelectorAll('div');
        for (const row of rows) {
          const text = getText(row);
          if (text.includes('총 상품 가격')) {
            const val = row.querySelector('em.final-product-price') || row.querySelector('em');
            summary.total_product_price = parsePrice(getText(val));
          }
          if (text.includes('총 배송비')) {
            const val = row.querySelector('em.final-product-price') || row.querySelector('em');
            summary.shipping_fee = parsePrice(getText(val));
          }
        }
      }

      return { items, summary };
    }
    """

    try:
        result = await page.evaluate(script)
        if not isinstance(result, dict):
            return {"items": [], "summary": {}}
        return result
    except Exception:
        return {"items": [], "summary": {}}

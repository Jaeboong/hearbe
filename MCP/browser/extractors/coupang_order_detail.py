"""
Coupang order detail extraction.
"""

from __future__ import annotations

from typing import Dict, Any


ACTION_LABELS = [
    "장바구니 담기",
    "배송 조회",
    "주문, 배송 취소",
    "주문내역 삭제",
    "주문목록 돌아가기",
]


async def extract_coupang_order_detail(page) -> Dict[str, Any]:
    script = r"""
    () => {
      const ACTION_LABELS = [
        "장바구니 담기",
        "배송 조회",
        "주문, 배송 취소",
        "주문내역 삭제",
        "주문목록 돌아가기",
      ];
      const getText = (el) => (el && (el.innerText || el.textContent) || '').trim();
      const normalize = (text) => String(text || '')
        .replace(/[\s·\.\-]+/g, '')
        .replace(/[^0-9A-Za-z가-힣]/g, '');

      const parseNumber = (value) => {
        if (value === null || value === undefined) return null;
        const cleaned = String(value).replace(/[^\d]/g, '');
        if (!cleaned) return null;
        const num = parseInt(cleaned, 10);
        return Number.isNaN(num) ? null : num;
      };
      const formatPrice = (value) => {
        const num = typeof value === 'number' ? value : parseNumber(value);
        if (num === null) return '';
        return `${num.toLocaleString('ko-KR')}원`;
      };

      const dataEl = document.querySelector('script#__NEXT_DATA__');
      let data = null;
      if (dataEl && dataEl.textContent) {
        try { data = JSON.parse(dataEl.textContent); } catch (e) { data = null; }
      }

      const domains = data?.props?.pageProps?.domains || {};
      const thankYouModel = domains?.thankYou?.thankYouPageModel || null;

      const order = thankYouModel?.order || {};
      const payment = thankYouModel?.payment || {};
      const member = thankYouModel?.member || {};
      const delivery = order?.deliveryDestination || {};

      const items = [];
      const bundleGroups = order?.bundleGroupList || [];
      for (const bundle of bundleGroups) {
        const groups = bundle?.groupList || [];
        for (const group of groups) {
          const products = group?.productList || [];
          for (const product of products) {
            if (!product) continue;
            items.push({
              product_name: product.productName || '',
              vendor_item_name: product.vendorItemName || '',
              quantity: product.quantity ?? null,
              unit_price: product.unitPrice ?? null,
              discounted_unit_price: product.discountedUnitPrice ?? null,
              image: product.imagePath || '',
              vendor_name: group?.vendor?.vendorName || '',
            });
          }
        }
      }

      const payed = payment?.payedPayment || {};
      const rocketBank = payed?.rocketBankPayment || {};

      const orderData = {
        order: {
          title: order?.title || '',
          ordered_at: order?.orderedAt ?? null,
        },
        items,
        delivery: {
          zip_code: delivery?.zipCode || '',
          address: delivery?.address || '',
          address_main: delivery?.addressMain || '',
          address_detail: delivery?.addressDetail || '',
          shipping_message: delivery?.shippingMessage?.normalMessage || '',
        },
        payment: {
          total_payed_amount: payment?.totalPayedAmount ?? null,
          total_order_amount: payment?.totalOrderAmount ?? null,
          total_product_price: payment?.totalProductPrice ?? null,
          main_pay_type: payment?.mainPayType || '',
          bank_name: rocketBank?.bankName || '',
          payed_price: rocketBank?.payedPrice ?? null,
          paid_at: payment?.paidAt ?? null,
        },
        member: {
          member_id: member?.memberId || '',
          name: member?.name || '',
        },
      };

      const bodyText = getText(document.body || document.documentElement);
      const normalized = normalize(bodyText);
      const actions = ACTION_LABELS.filter((label) => normalized.includes(normalize(label)));
      orderData.actions = actions.length ? actions : ACTION_LABELS.slice();

      const textData = {};
      const orderDateMatch = bodyText.match(/주문(?:일자|날짜|일시)\s*([0-9]{4}[.\-/년 ]\s*[0-9]{1,2}[.\-/월 ]\s*[0-9]{1,2}[일]?(?:\s*[0-9]{1,2}:[0-9]{2})?)/);
      if (orderDateMatch) textData.order_date = orderDateMatch[1].replace(/\s+/g, ' ').trim();
      const statusMatch = bodyText.match(/(배송중|배송완료|배송준비|상품준비|주문완료)/);
      if (statusMatch) textData.status = statusMatch[1];
      const etaMatch = bodyText.match(/(오늘|내일)\([^\)]+\)\s*도착\s*보장/);
      if (etaMatch) textData.eta = etaMatch[0];
      if (!textData.eta) {
        const etaMatch2 = bodyText.match(/([0-9]{1,2}[./월]\s*[0-9]{1,2}[일]?\s*\([^\)]+\)\s*도착\s*(?:예정|보장)?)/);
        if (etaMatch2) textData.eta = etaMatch2[1].replace(/\s+/g, ' ').trim();
      }
      if (!textData.eta) {
        const etaMatch3 = bodyText.match(/도착\s*(?:예정|보장)\s*[:：]?\s*([^\n\r]+?)(?=\s{2,}|\n|$)/);
        if (etaMatch3) textData.eta = etaMatch3[1].replace(/\s+/g, ' ').trim();
      }
      const totalMatch = bodyText.match(/총\s*결제금액\s*([\d,]+)\s*원/);
      if (totalMatch) textData.total_price = `${totalMatch[1]}원`;
      const recipientMatch = bodyText.match(/받는사람\s*([가-힣A-Za-z\*]+)/);
      if (recipientMatch) textData.recipient_name = recipientMatch[1];
      const phoneMatch = bodyText.match(/연락처\s*([0-9\-]+)/);
      if (phoneMatch) textData.recipient_phone = phoneMatch[1];
      const addrMatch = bodyText.match(/받는주소\s*\((\d+)\)\s*([^\t]+)/);
      if (addrMatch) textData.recipient_address = `(${addrMatch[1]}) ${addrMatch[2].trim()}`;
      orderData.text = textData;

      if (!orderData.payment.total_payed_amount && textData.total_price) {
        orderData.payment.total_payed_amount = parseNumber(textData.total_price);
      }

      const deliveryRecipientName = delivery?.receiverName || delivery?.receiver || delivery?.recipientName || '';
      const deliveryRecipientPhone = delivery?.receiverPhoneNumber || delivery?.receiverMobileNumber || delivery?.receiverPhone || '';
      const deliveryRecipientAddress = [delivery?.addressMain || delivery?.address || '', delivery?.addressDetail || '']
        .filter(Boolean)
        .join(' ')
        .trim();
      const recipientName = textData.recipient_name || deliveryRecipientName || '';
      const recipientPhone = textData.recipient_phone || deliveryRecipientPhone || '';
      const recipientAddress = textData.recipient_address || deliveryRecipientAddress || '';

      orderData.delivery.status = textData.status || orderData.delivery.status || '';
      orderData.delivery.eta = textData.eta || orderData.delivery.eta || '';

      const itemNames = items
        .map((item) => item.product_name || item.vendor_item_name || '')
        .filter((name) => name);
      const totalPriceText = textData.total_price
        || formatPrice(orderData.payment.total_payed_amount)
        || formatPrice(orderData.payment.total_order_amount)
        || formatPrice(orderData.payment.total_product_price);

      orderData.recipient = {
        name: recipientName,
        phone: recipientPhone,
        address: recipientAddress,
      };

      orderData.summary = {
        order_date: textData.order_date || orderData.order.ordered_at || '',
        status: textData.status || '',
        eta: textData.eta || '',
        item_names: itemNames,
        total_price: totalPriceText || '',
        recipient_name: recipientName,
        recipient_phone: recipientPhone,
        recipient_address: recipientAddress,
      };

      const speechParts = [];
      if (orderData.summary.order_date) speechParts.push(`주문 날짜 ${orderData.summary.order_date}`);
      if (orderData.summary.status) speechParts.push(`배송 상태 ${orderData.summary.status}`);
      if (orderData.summary.eta) speechParts.push(`도착 날짜 ${orderData.summary.eta}`);
      if (itemNames.length) speechParts.push(`주문 상품 ${itemNames.join(', ')}`);
      if (orderData.summary.total_price) speechParts.push(`가격 ${orderData.summary.total_price}`);
      const recipientParts = [];
      if (recipientName) recipientParts.push(recipientName);
      if (recipientPhone) recipientParts.push(`연락처 ${recipientPhone}`);
      if (recipientAddress) recipientParts.push(`주소 ${recipientAddress}`);
      if (recipientParts.length) speechParts.push(`받는사람 정보 ${recipientParts.join(', ')}`);
      orderData.speech = speechParts.join(', ');

      return orderData;
    }
    """

    try:
        result = await page.evaluate(script)
        if not isinstance(result, dict):
            return {"order": {}, "items": [], "payment": {}, "delivery": {}, "member": {}, "actions": ACTION_LABELS}
        return result
    except Exception:
        return {"order": {}, "items": [], "payment": {}, "delivery": {}, "member": {}, "actions": ACTION_LABELS}

"""Human reviewed KTK support center copy: three storefront languages.

All support requests are stored in the existing owner ticket queue.
"""

SUBJECTS = (
    ("پیگیری سفارش", "track_order"),
    ("مشاوره خرید و محصولات", "product_question"),
    ("ارسال و تحویل", "shipping"),
    ("لغو و مرجوعی", "return"),
    ("خرید عمده و همکاری", "wholesale"),
    ("سایر موارد", "other"),
)

_COPY = {
    "fa": {
        "page_title":"مرکز پشتیبانی کاتیکا", "page_intro":"برای پیگیری سفارش، ثبت درخواست، سوالات متداول و ارتباط با تیم پشتیبانی",
        "quick_ticket":"ثبت تیکت", "quick_ticket_info":"ثبت درخواست و دریافت پاسخ", "quick_track":"پیگیری سفارش", "quick_track_info":"پیگیری با شماره سفارش",
        "quick_faq":"سوالات متداول", "quick_faq_info":"پاسخ به پرسش‌های رایج شما", "quick_contact":"ارتباط سریع", "quick_contact_info":"راه‌های تماس با تیم پشتیبانی",
        "form_title":"ثبت درخواست پشتیبانی", "form_intro":"سوال یا درخواست خود را در فرم ثبت کنید. تیم پشتیبانی پس از بررسی، از طریق اطلاعات تماس ثبت‌شده با شما ارتباط خواهد گرفت.",
        "name":"نام و نام خانوادگی", "phone":"شماره تماس", "email":"ایمیل", "order_number":"شماره سفارش (اختیاری)",
        "order_example":"مثال: KTK-129456", "subject":"موضوع درخواست", "choose_subject":"انتخاب موضوع درخواست", "body":"شرح درخواست", "body_hint":"توضیحات خود را به طور کامل وارد کنید ...",
        "submit":"ارسال درخواست", "optional":"اختیاری", "required":"فیلد الزامی", "remaining":"نویسه",
        "contact_title":"راه‌های ارتباط با پشتیبانی", "contact_phone":"تلفن پشتیبانی", "contact_email":"ایمیل پشتیبانی", "hours_title":"ساعات پاسخ‌گویی", "hours_text":"برای اطلاع از ساعات پاسخ‌گویی با ما تماس بگیرید", "not_available":"هنوز ثبت نشده",
        "guide_order":"راهنمای پیگیری سفارش", "guide_order_sub":"شماره سفارش خود را در فرم ثبت کنید", "guide_products":"راهنمای خرید و محصولات", "guide_products_sub":"مشخصات محصولات و نکات انتخاب",
        "faq_title":"سوالات متداول", "faq_1":"زمان ارسال سفارش چقدر است؟", "faq_1_answer":"زمان ارسال به مقصد و شیوه ارسال بستگی دارد. برای اطلاع از وضعیت دقیق، شماره سفارش خود را در فرم پشتیبانی ثبت کنید.",
        "faq_2":"شرایط مرجوعی کالا به چه صورت است؟", "faq_2_answer":"برای بررسی درخواست لغو یا مرجوعی، شماره سفارش و توضیحات خود را در فرم پشتیبانی ثبت کنید. نتیجه پس از بررسی اعلام خواهد شد.",
        "faq_3":"آیا امکان خرید عمده و همکاری وجود دارد؟", "faq_3_answer":"برای استعلام خرید عمده و همکاری تجاری از صفحه همکاری با ما درخواست خود را ثبت کنید.",
        "faq_4":"چگونه می‌توانم وضعیت سفارش خود را پیگیری کنم؟", "faq_4_answer":"موضوع «پیگیری سفارش» را انتخاب کنید و شماره سفارش را همراه اطلاعات تماس وارد کنید.",
        "faq_5":"هزینه و شرایط ارسال سفارش‌ها چگونه است؟", "faq_5_answer":"هزینه و شرایط ارسال بر اساس سفارش و مقصد تعیین می‌شود؛ برای جزئیات با پشتیبانی در ارتباط باشید.",
        "form_error":"لطفاً موارد مشخص‌شده را اصلاح کنید.",
    },
    "en": {
        "page_title":"KTK Support Center", "page_intro":"Order follow-up, support requests, frequently asked questions and contact options",
        "quick_ticket":"Submit a ticket", "quick_ticket_info":"Send a request and receive a response", "quick_track":"Track an order", "quick_track_info":"Follow up using your order number",
        "quick_faq":"FAQs", "quick_faq_info":"Answers to common questions", "quick_contact":"Quick contact", "quick_contact_info":"Ways to reach our support team",
        "form_title":"Submit a support request", "form_intro":"Send your question or request using this form. Our team will follow up using your contact details after reviewing it.",
        "name":"Full name", "phone":"Phone number", "email":"Email", "order_number":"Order number (optional)",
        "order_example":"Example: KTK-129456", "subject":"Request subject", "choose_subject":"Choose a subject", "body":"Request details", "body_hint":"Describe your request in detail ...",
        "submit":"Send request", "optional":"Optional", "required":"Required", "remaining":"characters",
        "contact_title":"Contact our support team", "contact_phone":"Support phone", "contact_email":"Support email", "hours_title":"Support hours", "hours_text":"Contact us for current support hours", "not_available":"Not provided yet",
        "guide_order":"Order follow-up guide", "guide_order_sub":"Enter your order number in the form", "guide_products":"Product and purchase guide", "guide_products_sub":"Product details and selection tips",
        "faq_title":"Frequently asked questions", "faq_1":"How long does delivery take?", "faq_1_answer":"Delivery depends on your destination and shipping method. Submit your order number to check its status.",
        "faq_2":"How do returns work?", "faq_2_answer":"Enter your order number and reason in the support form. Our team will review your request and reply.",
        "faq_3":"Can I request wholesale purchases or cooperation?", "faq_3_answer":"Use our cooperation page to inquire about bulk orders and partnerships.",
        "faq_4":"How can I track my order?", "faq_4_answer":"Select 'Track an order' and provide the order number and your contact information.",
        "faq_5":"How are shipping charges calculated?", "faq_5_answer":"Delivery terms and costs depend on the order and destination. Please contact support for details.",
        "form_error":"Please correct the highlighted fields.",
    },
    "zh-hans": {
        "page_title":"KTK 客服中心", "page_intro":"订单查询、提交支持请求、常见问题及联系方式",
        "quick_ticket":"提交工单", "quick_ticket_info":"提交请求并获得回复", "quick_track":"查询订单", "quick_track_info":"使用订单号进行查询",
        "quick_faq":"常见问题", "quick_faq_info":"解答常见疑问", "quick_contact":"快速联系", "quick_contact_info":"联系我们的客服团队",
        "form_title":"提交支持请求", "form_intro":"请填写您的问题或请求。客服团队审核后将通过您提供的联系方式联系您。",
        "name":"姓名", "phone":"联系电话", "email":"电子邮箱", "order_number":"订单号（选填）",
        "order_example":"例如：KTK-129456", "subject":"请求主题", "choose_subject":"选择请求主题", "body":"请求详情", "body_hint":"请详细描述您的问题……",
        "submit":"发送请求", "optional":"选填", "required":"必填", "remaining":"字符",
        "contact_title":"联系客服", "contact_phone":"客服电话", "contact_email":"客服邮箱", "hours_title":"服务时间", "hours_text":"请联系我们以了解服务时间", "not_available":"暂未提供",
        "guide_order":"订单查询指南", "guide_order_sub":"在表单中填写订单号", "guide_products":"购买及产品指南", "guide_products_sub":"产品信息和选购提示",
        "faq_title":"常见问题", "faq_1":"订单需要多久送达？", "faq_1_answer":"配送时间取决于目的地和配送方式。请填写订单号查询进度。",
        "faq_2":"如何申请退货？", "faq_2_answer":"请在客服表单中填写订单号和原因，客服审核后会与您联系。",
        "faq_3":"是否提供批量采购和合作？", "faq_3_answer":"如需批量采购或合作，请通过合作页面提交申请。",
        "faq_4":"如何查询订单状态？", "faq_4_answer":"请选择“查询订单”，并填写订单号及联系方式。",
        "faq_5":"运费及配送条件如何确定？", "faq_5_answer":"运费和配送条件取决于订单和目的地，请联系客服了解详情。",
        "form_error":"请修改标记的字段。",
    },
}

_SUBJECT_LABELS = {
    "fa": ("پیگیری سفارش", "مشاوره خرید و محصولات", "ارسال و تحویل", "لغو و مرجوعی", "خرید عمده و همکاری", "سایر موارد"),
    "en": ("Track an order", "Product advice", "Shipping and delivery", "Cancellations and returns", "Wholesale and cooperation", "Other"),
    "zh-hans": ("订单查询", "产品咨询", "配送与交付", "取消与退货", "批发与合作", "其他"),
}


def support_context(language):
    language = (language or "fa").lower()
    language = "zh-hans" if language.startswith("zh") else "en" if language.startswith("en") else "fa"
    return _COPY[language], [
        {"value": value, "label": label}
        for (value, _), label in zip(SUBJECTS, _SUBJECT_LABELS[language])
    ]

(() => {
  'use strict';

  const messages = {
    ur: {
      skipLink: 'مرکزی حصے پر جائیں', mainNavigation: 'مرکزی فہرست', homeLabel: 'مویشی محافظ کا مرکزی صفحہ', openMenu: 'فہرست کھولیں', closeMenu: 'فہرست بند کریں',
      home: 'مرکزی صفحہ', howItWorks: 'یہ کیسے کام کرتا ہے', features: 'خاص باتیں', languageLabel: 'زبان منتخب کریں', login: 'لاگ اِن', getStarted: 'شروع کریں', seeHowItWorks: 'دیکھیں یہ کیسے کام کرتا ہے',
      eyebrow: 'مویشیوں کی صحت، آسان زبان میں', heroTitle: 'بیماری کی علامات جلد پہچانیں، بروقت قدم اٹھائیں۔',
      heroSupport: 'جانور کی تصویر شامل کریں، علامات بتائیں، اور ممکنہ بیماری اور فوری توجہ کی ضرورت کے بارے میں آسان AI رہنمائی حاصل کریں۔',
      heroCaution: 'یہ ابتدائی رہنمائی ہے، حتمی تشخیص نہیں۔',
      journeyLabel: 'صحت کی جانچ کا طریقہ', journeyPhoto: 'تصویر اور علامات', journeyUrgency: 'فوری توجہ کی پہچان', journeyUrdu: 'آسان اردو رہنمائی',
      heroVisualLabel: 'پاکستانی کسان اپنے جانور کے ساتھ مویشی محافظ استعمال کرتے ہوئے', healthCheck: 'صحت کی جانچ', photoReady: 'صاف تصویر شامل ہے', reportedSymptoms: 'بتائی گئی علامات',
      demoSymptoms: 'کھانا کم، چلنے میں سستی', attentionLevel: 'توجہ کی سطح', vetReviewAdvised: 'ڈاکٹر سے جلد مشورہ کریں', preliminaryOnly: 'ابتدائی AI رہنمائی',
      simpleProcess: 'سادہ طریقہ', howHeading: 'چار آسان قدم', howSupport: 'جانور کا ریکارڈ بنانے سے لے کر صحت کی پچھلی تفصیل محفوظ رکھنے تک۔',
      stepOneTitle: 'اپنا جانور شامل کریں', stepOneText: 'نام، قسم اور بنیادی معلومات محفوظ کریں۔', stepTwoTitle: 'تصویر اور علامات دیں',
      stepTwoText: 'صاف تصویر کے ساتھ جو علامات نظر آئیں وہ لکھیں۔', stepThreeTitle: 'ابتدائی AI رہنمائی پائیں', stepThreeText: 'ممکنہ بیماری اور توجہ کی ضرورت سمجھیں۔',
      stepFourTitle: 'ریکارڈ محفوظ رکھیں', stepFourText: 'نتیجہ محفوظ کریں اور وقت کے ساتھ صحت دیکھیں۔', builtForFarmers: 'کسانوں کے لیے بنایا گیا',
      differenceHeading: 'مویشی محافظ کیوں مختلف ہے؟', differenceSupport: 'صرف ضروری مدد—تاکہ کسان جلد سمجھ سکے اور محفوظ قدم اٹھا سکے۔',
      screeningTitle: 'تصویر اور علامات کی مشترکہ جانچ', screeningText: 'AI کی مدد سے دونوں معلومات کو ایک ساتھ سمجھنے کی ابتدائی کوشش۔',
      redFlagTitle: 'خطرے کی علامات پر توجہ', redFlagText: 'فوری مدد کی ضرورت کو واضح انداز میں نمایاں کرنا۔', urduTitle: 'اردو پہلے، آواز کے لیے تیار',
      urduText: 'سادہ زبان جو موبائل پر پڑھنے اور سننے میں آسان ہو۔', recordsTitle: 'بچاؤ اور صحت کا ریکارڈ', recordsText: 'صحت کی اہم معلومات منظم رکھنے کے لیے ایک واضح جگہ۔',
      healthPassportLabel: 'ہیلتھ پاسپورٹ', passportHeading: 'بہتر ریکارڈ۔ بہتر دیکھ بھال۔ زیادہ بھروسا۔',
      passportText: 'مویشی محافظ ہر جانور کی صحت کی تفصیل منظم رکھتا ہے۔ مستقبل میں کسان ایک آسان ہیلتھ کارڈ اپنی مرضی سے خریدار کے ساتھ بھی شیئر کر سکے گا۔',
      passportFuture: 'یہ حصہ آئندہ ہیلتھ پاسپورٹ کے تصور کی نمائشی جھلک ہے۔', passportDemoLabel: 'نمائشی ہیلتھ پاسپورٹ', demoCow: 'گائے', demoLabel: 'نمونہ',
      vaccinationStatus: 'ویکسین کی حالت', dewormingStatus: 'کیڑوں کی دوا', previousAssessments: 'پچھلے معائنے', followUpStatus: 'دوبارہ جانچ کی حالت',
      activeWarnings: 'موجودہ صحت کی تنبیہ', demoRecorded: 'ریکارڈ موجود', demoHistory: 'محفوظ تاریخ', demoUpToDate: 'معلومات مکمل', demoNoWarning: 'کوئی تنبیہ نہیں',
      safetyText: 'مویشی محافظ ابتدائی صحت جانچ اور آگاہی میں مدد دیتا ہے۔ نتائج ممکنہ بیماریوں کی نشاندہی کرتے ہیں اور جانوروں کے ماہر ڈاکٹر کا متبادل نہیں۔',
      readyLabel: 'بہتر دیکھ بھال کی شروعات', finalHeading: 'اپنے جانوروں کا صحت ریکارڈ آج سے سنبھالیں۔',
      footerLine: 'مویشیوں کی صحت کے لیے آسان، محفوظ اور ذمہ دار رہنمائی۔'
    },
    en: {
      skipLink: 'Skip to main content', mainNavigation: 'Main navigation', homeLabel: 'Maweshi Muhafiz home', openMenu: 'Open menu', closeMenu: 'Close menu',
      home: 'Home', howItWorks: 'How It Works', features: 'Features', languageLabel: 'Choose language', login: 'Login', getStarted: 'Get Started', seeHowItWorks: 'See How It Works',
      eyebrow: 'Livestock health, in language farmers understand', heroTitle: 'Spot health problems earlier. Act with confidence.',
      heroSupport: 'Upload animal photos, describe the symptoms, and receive understandable AI-assisted guidance about possible conditions and urgency.',
      heroCaution: 'Preliminary guidance—not a guaranteed diagnosis.',
      journeyLabel: 'Health screening journey', journeyPhoto: 'Photos + symptoms', journeyUrgency: 'Urgency detection', journeyUrdu: 'Simple Urdu guidance',
      heroVisualLabel: 'Pakistani farmer using Maweshi Muhafiz beside his livestock', healthCheck: 'Health check', photoReady: 'Clear photo added', reportedSymptoms: 'Reported symptoms',
      demoSymptoms: 'Eating less, slow movement', attentionLevel: 'Urgency level', vetReviewAdvised: 'Consult a veterinarian soon', preliminaryOnly: 'Preliminary AI guidance',
      simpleProcess: 'A simple process', howHeading: 'Four clear steps', howSupport: 'From creating an animal record to keeping its health history organised.',
      stepOneTitle: 'Add your animal', stepOneText: 'Save its name, type, and essential details.', stepTwoTitle: 'Upload photos and describe symptoms',
      stepTwoText: 'Add a clear image and describe what you can observe.', stepThreeTitle: 'Receive AI-assisted guidance', stepThreeText: 'Understand possible conditions and the level of urgency.',
      stepFourTitle: 'Save and track over time', stepFourText: 'Keep the result and build a useful health history.', builtForFarmers: 'Built around farmers',
      differenceHeading: 'Why Maweshi Muhafiz is different', differenceSupport: 'Focused help that makes concerns easier to understand and safer to act on.',
      screeningTitle: 'Image + symptom health screening', screeningText: 'An AI-assisted first look that considers both sources together.',
      redFlagTitle: 'Emergency and Red-Flag awareness', redFlagText: 'Clear emphasis when signs may need urgent professional attention.', urduTitle: 'Urdu-first and voice accessible',
      urduText: 'Simple guidance designed to be readable and listenable on a phone.', recordsTitle: 'Preventive health records', recordsText: 'One organised place for important long-term health information.',
      healthPassportLabel: 'Health Passport', passportHeading: 'Better records. Better care. More trust.',
      passportText: 'Maweshi Muhafiz keeps an organised health history for each animal. In the future, a farmer may choose to share a simplified Health Card with buyers.',
      passportFuture: 'This is a presentation preview of the planned Health Passport experience.', passportDemoLabel: 'Demo Health Passport', demoCow: 'Cow', demoLabel: 'Demo',
      vaccinationStatus: 'Vaccination status', dewormingStatus: 'Deworming status', previousAssessments: 'Previous assessments', followUpStatus: 'Follow-up status',
      activeWarnings: 'Active health warnings', demoRecorded: 'Record available', demoHistory: 'History saved', demoUpToDate: 'Up to date', demoNoWarning: 'No active warning',
      safetyText: 'Maweshi Muhafiz supports early health screening and awareness. Results represent possible conditions and do not replace professional veterinary care.',
      readyLabel: 'Start with better care', finalHeading: 'Organise your animals’ health records from today.', footerLine: 'Clear, safe, and responsible guidance for livestock health.',
    }
  };

  const menuToggle = document.querySelector('#menu-toggle');
  const navLinks = document.querySelector('#nav-links');
  let language = window.MaweshiI18n.getLanguage();

  function t(key) { return messages[language][key] || key; }

  function applyLanguage(nextLanguage) {
    language = window.MaweshiI18n.applyPage(nextLanguage, messages).language;
    const isOpen = menuToggle.getAttribute('aria-expanded') === 'true';
    menuToggle.setAttribute('aria-label', t(isOpen ? 'closeMenu' : 'openMenu'));
  }

  function setMenu(open) {
    navLinks.classList.toggle('is-open', open);
    menuToggle.setAttribute('aria-expanded', String(open));
    menuToggle.setAttribute('aria-label', t(open ? 'closeMenu' : 'openMenu'));
  }

  menuToggle.addEventListener('click', () => setMenu(menuToggle.getAttribute('aria-expanded') !== 'true'));

  document.addEventListener('click', (event) => {
    const languageButton = event.target.closest('[data-language]');
    if (languageButton) applyLanguage(languageButton.dataset.language);
    if (event.target.closest('#nav-links a[href^="#"]')) setMenu(false);
  });

  document.addEventListener('keydown', (event) => { if (event.key === 'Escape') setMenu(false); });
  applyLanguage(language);
})();

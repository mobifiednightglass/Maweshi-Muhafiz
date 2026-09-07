(() => {
  'use strict';

  const API_BASE = 'http://127.0.0.1:5000';
  const OUTBREAK_INSIGHTS_ENDPOINT = `${API_BASE}/api/insights/area/outbreak`;
  const ALL_REGIONS = '__all__';
  const MAX_CONDITIONS = 5;

  const copy = {
    ur: {
      skipLink: 'مرکزی حصے پر جائیں', homeLabel: 'مویشی محافظ کا مرکزی صفحہ', languageLabel: 'زبان منتخب کریں', logout: 'لاگ آؤٹ', backToDashboard: 'ڈیش بورڈ پر واپس جائیں',
      kicker: 'گمنام کمیونٹی خلاصہ', pageTitle: 'علاقے کے حساب سے صحت معائنوں کی معلومات', pageIntro: 'رجسٹرڈ جانوروں کے محفوظ شدہ صحت معائنوں کا علاقائی خلاصہ۔ یہ اعداد کسی جانور یا مالک کی شناخت ظاہر نہیں کرتے۔', allTimeScope: 'تمام محفوظ شدہ معائنے',
      loadingLabel: 'علاقائی معلومات دیکھی جا رہی ہیں', tryAgain: 'دوبارہ کوشش کریں', connectionTitle: 'علاقائی معلومات ابھی دستیاب نہیں', connectionMessage: 'رابطہ نہیں ہو سکا۔ کچھ دیر بعد دوبارہ کوشش کریں۔', malformedTitle: 'علاقائی معلومات دکھائی نہیں جا سکیں', malformedMessage: 'جواب کی کچھ معلومات سمجھ نہیں آئیں۔ براہِ کرم دوبارہ کوشش کریں۔',
      emptyTitle: 'ابھی کمیونٹی معائنوں کی معلومات موجود نہیں', emptyMessage: 'صحت معائنے محفوظ ہونے کے بعد علاقائی خلاصہ یہاں نظر آئے گا۔', filtersLabel: 'معلومات کے فلٹر', regionFilter: 'علاقہ منتخب کریں', allRegions: 'تمام علاقے', regionNotRecorded: 'علاقہ درج نہیں', refresh: 'تازہ کریں',
      summaryLabel: 'علاقائی صحت معائنوں کا خلاصہ', regionGroups: 'علاقائی گروپ', totalAssessments: 'کل معائنے', flaggedAssessments: 'فوری یا نشان زدہ', flaggedShare: 'نشان زدہ معائنوں کا حصہ',
      flaggedActivityTitle: 'نشان زدہ معائنوں کی سرگرمی موجود ہے', flaggedActivityMessage: '{flagged} از {total} محفوظ شدہ معائنے فوری یا نشان زدہ ہیں۔ یہ وبا کی تنبیہ نہیں ہے۔', clearActivityTitle: 'نشان زدہ معائنہ موجود نہیں', clearActivityMessage: 'منتخب خلاصے میں کوئی معائنہ فوری یا نشان زدہ نہیں ہے۔',
      assessmentVolume: 'معائنوں کی تعداد', regionalComparison: 'علاقائی موازنہ', notFlagged: 'نشان زدہ نہیں', flaggedShort: 'نشان زدہ', comparisonHelp: 'یہ چارٹ صرف محفوظ شدہ معائنوں کی تعداد دکھاتا ہے، بیماری کی شرح یا علاقائی خطرہ نہیں۔', assessmentCountLabel: '{count} معائنے، {flagged} نشان زدہ',
      possibleConditions: 'ممکنہ حالتیں', conditionMentions: 'زیادہ درج ہونے والی ممکنہ حالتیں', conditionsHelp: 'یہ ابتدائی AI معائنوں میں درج ممکنہ حالتیں ہیں، تصدیق شدہ بیماریاں نہیں۔ ایک معائنے میں ایک سے زیادہ حالتیں ہو سکتی ہیں۔', noConditions: 'منتخب معلومات میں ممکنہ حالتیں درج نہیں ہیں۔', conditionCountLabel: '{count} بار، {flagged} نشان زدہ',
      scopeTitle: 'ان اعداد کو کیسے سمجھیں', scopeMessage: 'یہ گمنام مجموعی اعداد تمام صارفین کے جانوروں کے محفوظ شدہ معائنوں سے بنتے ہیں۔ یہ منفرد جانوروں یا کسانوں کی تعداد، بیماری کی شرح، وقت کے ساتھ رجحان یا وبا کی تصدیق نہیں کرتے۔',
      footerCare: 'مویشیوں کی بہتر دیکھ بھال میں آپ کی مدد کے لیے۔', footerDisclaimer: 'AI کی رائے ابتدائی رہنمائی ہے، ڈاکٹر کا متبادل نہیں۔'
    },
    en: {
      skipLink: 'Skip to main content', homeLabel: 'Maweshi Muhafiz home', languageLabel: 'Choose language', logout: 'Logout', backToDashboard: 'Back to Dashboard',
      kicker: 'Anonymized community snapshot', pageTitle: 'Health-assessment activity by region', pageIntro: 'A regional summary of saved health assessments for registered animals. These figures do not identify an animal or owner.', allTimeScope: 'All saved assessments',
      loadingLabel: 'Loading regional insights', tryAgain: 'Try again', connectionTitle: 'Regional insights are unavailable right now', connectionMessage: 'We could not connect. Please try again in a little while.', malformedTitle: 'Regional insights could not be displayed', malformedMessage: 'Some response information could not be understood. Please try again.',
      emptyTitle: 'No community assessment activity yet', emptyMessage: 'The regional snapshot will appear after health assessments are saved.', filtersLabel: 'Insight filters', regionFilter: 'Choose a region', allRegions: 'All regions', regionNotRecorded: 'Region not recorded', refresh: 'Refresh',
      summaryLabel: 'Regional health-assessment summary', regionGroups: 'Region groups', totalAssessments: 'Total assessments', flaggedAssessments: 'Urgent or flagged', flaggedShare: 'Flagged assessment share',
      flaggedActivityTitle: 'Flagged assessment activity recorded', flaggedActivityMessage: '{flagged} of {total} saved assessments are urgent or flagged. This is not an outbreak warning.', clearActivityTitle: 'No flagged assessments recorded', clearActivityMessage: 'No assessment in the selected snapshot is urgent or flagged.',
      assessmentVolume: 'Assessment volume', regionalComparison: 'Regional comparison', notFlagged: 'Not flagged', flaggedShort: 'Flagged', comparisonHelp: 'This chart compares saved assessment volume only—not disease prevalence or regional risk.', assessmentCountLabel: '{count} assessments, {flagged} flagged',
      possibleConditions: 'Possible conditions', conditionMentions: 'Most-mentioned possible conditions', conditionsHelp: 'These are possible conditions from preliminary AI assessments, not confirmed diseases. One assessment may mention more than one condition.', noConditions: 'No possible conditions are recorded in the selected data.', conditionCountLabel: '{count} mentions, {flagged} flagged',
      scopeTitle: 'How to read these figures', scopeMessage: 'These anonymized aggregates use saved assessments for animals across all users. They do not represent unique animals or farmers, disease prevalence, change over time, or confirmation of an outbreak.',
      footerCare: 'Built to support better livestock care.', footerDisclaimer: 'AI guidance is preliminary and does not replace a veterinarian.'
    }
  };

  const el = {
    loading: document.querySelector('#insights-loading'), error: document.querySelector('#insights-error'), empty: document.querySelector('#insights-empty'), content: document.querySelector('#insights-content'),
    errorTitle: document.querySelector('#error-title'), errorMessage: document.querySelector('#error-message'), retry: document.querySelector('#retry-insights'), refresh: document.querySelector('#refresh-insights'), filter: document.querySelector('#region-filter'),
    regionCount: document.querySelector('#region-count'), assessmentCount: document.querySelector('#assessment-count'), flaggedCount: document.querySelector('#flagged-count'), flaggedShare: document.querySelector('#flagged-share'),
    activity: document.querySelector('#activity-notice'), activityMark: document.querySelector('.activity-notice-mark'), activityTitle: document.querySelector('#activity-title'), activityMessage: document.querySelector('#activity-message'),
    regionChart: document.querySelector('#region-chart'), conditionsList: document.querySelector('#conditions-list'), conditionsEmpty: document.querySelector('#conditions-empty')
  };

  let language = window.MaweshiI18n.getLanguage();
  let insights = [];
  let selectedRegion = ALL_REGIONS;
  let errorKind = null;

  function t(key, values = {}) {
    let value = copy[language][key] || key;
    Object.entries(values).forEach(([name, replacement]) => { value = value.replace(`{${name}}`, replacement); });
    return value;
  }

  function number(value) {
    return new Intl.NumberFormat(language === 'ur' ? 'ur-PK' : 'en-PK').format(value);
  }

  function percentage(value) {
    return new Intl.NumberFormat(language === 'ur' ? 'ur-PK' : 'en-PK', { style: 'percent', maximumFractionDigits: 1 }).format(value);
  }

  function regionLabel(value) {
    return value.trim().toLowerCase() === 'unknown' ? t('regionNotRecorded') : value;
  }

  function validMetric(value) {
    return value && typeof value === 'object' && !Array.isArray(value)
      && Number.isInteger(value.total) && value.total >= 0
      && Number.isInteger(value.flagged) && value.flagged >= 0
      && value.flagged <= value.total;
  }

  function validInsight(entry) {
    return entry && typeof entry === 'object' && !Array.isArray(entry)
      && typeof entry.region === 'string' && entry.region.trim()
      && Number.isInteger(entry.total_assessments) && entry.total_assessments >= 0
      && Number.isInteger(entry.flagged_cases) && entry.flagged_cases >= 0
      && entry.flagged_cases <= entry.total_assessments
      && entry.conditions && typeof entry.conditions === 'object' && !Array.isArray(entry.conditions)
      && Object.entries(entry.conditions).every(([name, metric]) => name.trim() && validMetric(metric));
  }

  function selectedEntries() {
    return selectedRegion === ALL_REGIONS ? insights : insights.filter((entry) => entry.region === selectedRegion);
  }

  function summary(entries) {
    return entries.reduce((result, entry) => ({
      total: result.total + entry.total_assessments,
      flagged: result.flagged + entry.flagged_cases
    }), { total: 0, flagged: 0 });
  }

  function aggregateConditions(entries) {
    const result = {};
    entries.forEach((entry) => {
      Object.entries(entry.conditions).forEach(([name, metric]) => {
        if (!result[name]) result[name] = { total: 0, flagged: 0 };
        result[name].total += metric.total;
        result[name].flagged += metric.flagged;
      });
    });
    return Object.entries(result)
      .sort((a, b) => b[1].total - a[1].total || a[0].localeCompare(b[0]))
      .slice(0, MAX_CONDITIONS);
  }

  function rebuildFilter() {
    const options = [{ value: ALL_REGIONS, label: t('allRegions') }, ...insights.map((entry) => ({ value: entry.region, label: regionLabel(entry.region) }))];
    if (!options.some((option) => option.value === selectedRegion)) selectedRegion = ALL_REGIONS;
    const fragment = document.createDocumentFragment();
    options.forEach((option) => {
      const node = document.createElement('option');
      node.value = option.value;
      node.textContent = option.label;
      node.dir = option.value === ALL_REGIONS || option.value.toLowerCase() === 'unknown' ? '' : 'auto';
      fragment.appendChild(node);
    });
    el.filter.replaceChildren(fragment);
    el.filter.value = selectedRegion;
  }

  function renderRegionChart(entries) {
    const maxTotal = Math.max(...entries.map((entry) => entry.total_assessments), 1);
    const fragment = document.createDocumentFragment();
    entries.forEach((entry) => {
      const row = document.createElement('article');
      row.className = 'region-chart-row';
      const label = document.createElement('div');
      label.className = 'region-chart-label';
      const name = document.createElement('strong');
      name.textContent = regionLabel(entry.region);
      name.dir = entry.region.toLowerCase() === 'unknown' ? '' : 'auto';
      const count = document.createElement('span');
      count.textContent = t('assessmentCountLabel', { count: number(entry.total_assessments), flagged: number(entry.flagged_cases) });
      label.append(name, count);

      const track = document.createElement('div');
      track.className = 'region-chart-track';
      const combined = document.createElement('div');
      combined.className = 'region-chart-combined';
      combined.style.width = `${(entry.total_assessments / maxTotal) * 100}%`;
      const normal = document.createElement('span');
      normal.className = 'region-chart-normal';
      normal.style.width = `${entry.total_assessments ? ((entry.total_assessments - entry.flagged_cases) / entry.total_assessments) * 100 : 0}%`;
      const flagged = document.createElement('span');
      flagged.className = 'region-chart-flagged';
      flagged.style.width = `${entry.total_assessments ? (entry.flagged_cases / entry.total_assessments) * 100 : 0}%`;
      combined.append(normal, flagged);
      track.appendChild(combined);
      track.setAttribute('role', 'img');
      track.setAttribute('aria-label', `${regionLabel(entry.region)}: ${t('assessmentCountLabel', { count: number(entry.total_assessments), flagged: number(entry.flagged_cases) })}`);
      row.append(label, track);
      fragment.appendChild(row);
    });
    el.regionChart.replaceChildren(fragment);
  }

  function renderConditions(entries) {
    const conditions = aggregateConditions(entries);
    el.conditionsEmpty.classList.toggle('hidden', conditions.length !== 0);
    const maxTotal = Math.max(...conditions.map(([, metric]) => metric.total), 1);
    const fragment = document.createDocumentFragment();
    conditions.forEach(([condition, metric]) => {
      const row = document.createElement('article');
      row.className = 'condition-row';
      const head = document.createElement('div');
      head.className = 'condition-row-head';
      const name = document.createElement('strong');
      name.textContent = condition;
      name.dir = 'auto';
      const count = document.createElement('span');
      count.textContent = t('conditionCountLabel', { count: number(metric.total), flagged: number(metric.flagged) });
      head.append(name, count);
      const track = document.createElement('div');
      track.className = 'condition-track';
      const fill = document.createElement('div');
      fill.className = 'condition-fill';
      fill.style.width = `${(metric.total / maxTotal) * 100}%`;
      track.appendChild(fill);
      row.append(head, track);
      fragment.appendChild(row);
    });
    el.conditionsList.replaceChildren(fragment);
  }

  function renderContent() {
    const entries = selectedEntries();
    const totals = summary(entries);
    el.regionCount.textContent = number(entries.length);
    el.assessmentCount.textContent = number(totals.total);
    el.flaggedCount.textContent = number(totals.flagged);
    el.flaggedShare.textContent = percentage(totals.total ? totals.flagged / totals.total : 0);

    const hasFlagged = totals.flagged > 0;
    el.activity.classList.toggle('is-clear', !hasFlagged);
    el.activityMark.textContent = hasFlagged ? '!' : '✓';
    el.activityTitle.textContent = t(hasFlagged ? 'flaggedActivityTitle' : 'clearActivityTitle');
    el.activityMessage.textContent = hasFlagged
      ? t('flaggedActivityMessage', { flagged: number(totals.flagged), total: number(totals.total) })
      : t('clearActivityMessage');
    renderRegionChart(entries);
    renderConditions(entries);
  }

  function showError(kind) {
    errorKind = kind;
    el.loading.classList.add('hidden');
    el.empty.classList.add('hidden');
    el.content.classList.add('hidden');
    el.error.classList.remove('hidden');
    el.errorTitle.textContent = t(`${kind}Title`);
    el.errorMessage.textContent = t(`${kind}Message`);
  }

  async function loadInsights() {
    errorKind = null;
    el.error.classList.add('hidden');
    el.empty.classList.add('hidden');
    el.content.classList.add('hidden');
    el.loading.classList.remove('hidden');
    el.retry.disabled = true;
    el.refresh.disabled = true;
    try {
      const data = await window.MaweshiAuth.request(OUTBREAK_INSIGHTS_ENDPOINT, { headers: { Accept: 'application/json' } });
      if (!Array.isArray(data) || !data.every(validInsight)) { showError('malformed'); return; }
      insights = data;
      el.loading.classList.add('hidden');
      if (!data.length) { el.empty.classList.remove('hidden'); return; }
      rebuildFilter();
      renderContent();
      el.content.classList.remove('hidden');
    } catch (error) {
      console.error('Community area insights could not be loaded.', error);
      showError('connection');
    } finally {
      el.retry.disabled = false;
      el.refresh.disabled = false;
    }
  }

  function applyLanguage(nextLanguage) {
    language = window.MaweshiI18n.applyPage(nextLanguage, copy).language;
    document.title = language === 'ur' ? 'Maweshi Muhafiz | علاقائی صحت کی معلومات' : 'Maweshi Muhafiz | Community Area Insights';
    if (insights.length) {
      rebuildFilter();
      renderContent();
    }
    if (errorKind) showError(errorKind);
  }

  document.addEventListener('click', (event) => {
    const languageButton = event.target.closest('[data-language]');
    if (languageButton) applyLanguage(languageButton.dataset.language);
  });
  el.filter.addEventListener('change', () => { selectedRegion = el.filter.value; renderContent(); });
  el.retry.addEventListener('click', loadInsights);
  el.refresh.addEventListener('click', loadInsights);

  applyLanguage(language);
  loadInsights();
})();

const fs = require('fs');

function processFile(filePath, transforms) {
    let content = fs.readFileSync(filePath, 'utf8');
    transforms.forEach(t => {
        content = content.replace(t.search, t.replace);
    });
    fs.writeFileSync(filePath, content);
}

// 1. ResultsPage.jsx
processFile('d:/ML-PROJECT-SEM-5/frontend/src/pages/Results/ResultsPage.jsx', [
    { search: /text-slate-400/g, replace: 'text-stone-400' },
    { search: /text-slate-900/g, replace: 'text-stone-900' },
    { search: /border-slate-100/g, replace: 'border-stone-100' },
]);

// 2. ResultHero.jsx
processFile('d:/ML-PROJECT-SEM-5/frontend/src/components/results/ResultHero.jsx', [
    { search: /bg-emerald-100 text-emerald-700/g, replace: 'bg-emerald-50 text-emerald-700 border border-emerald-200' },
    { search: /bg-blue-100 text-blue-700/g, replace: 'bg-blue-50 text-blue-700 border border-blue-200' },
    { search: /bg-amber-100 text-amber-700/g, replace: 'bg-stone-100 text-stone-700 border border-stone-300' },
    { search: /bg-orange-100 text-orange-700/g, replace: 'bg-stone-100 text-stone-700 border border-stone-300' },
    { search: /bg-red-100 text-red-700/g, replace: 'bg-stone-50 text-stone-600 border border-stone-200' },
    { search: /bg-primary\/10/g, replace: 'bg-stone-100 border border-stone-200' },
    { search: /text-primary/g, replace: 'text-stone-900' },
    { search: /bg-primary/g, replace: 'bg-stone-900' },
    { search: /text-slate-500/g, replace: 'text-stone-500' },
    { search: /text-slate-900/g, replace: 'text-stone-900' },
    { search: /bg-slate-100/g, replace: 'bg-stone-100' },
]);

// 3. ConfidenceCard.jsx
processFile('d:/ML-PROJECT-SEM-5/frontend/src/components/results/ConfidenceCard.jsx', [
    { search: /shadow-\[0_8px_30px_rgb\(0,0,0,0\.06\)\]/g, replace: 'shadow-card' },
    { search: /bg-slate-50/g, replace: 'bg-stone-50' },
    { search: /text-slate-900/g, replace: 'text-stone-900' },
    { search: /text-slate-400/g, replace: 'text-stone-400' },
    { search: /text-slate-500/g, replace: 'text-stone-500' },
    { search: /bg-slate-100/g, replace: 'bg-stone-100' },
    { search: /bg-primary/g, replace: 'bg-stone-900' },
    { search: /text-emerald-500/g, replace: 'text-emerald-600' },
    { search: /text-blue-500/g, replace: 'text-blue-600' },
    { search: /text-amber-500/g, replace: 'text-stone-600' },
    { search: /bg-amber-50/g, replace: 'bg-stone-50' },
    { search: /text-amber-700/g, replace: 'text-stone-700' },
    { search: /text-orange-500/g, replace: 'text-stone-500' },
    { search: /bg-orange-50/g, replace: 'bg-stone-50' },
    { search: /text-orange-700/g, replace: 'text-stone-600' },
    { search: /text-red-500/g, replace: 'text-stone-400' },
    { search: /bg-red-50/g, replace: 'bg-stone-50' },
    { search: /text-red-700/g, replace: 'text-stone-500' },
]);

// 4. TopRecommendations.jsx
processFile('d:/ML-PROJECT-SEM-5/frontend/src/components/results/TopRecommendations.jsx', [
    { search: /border-primary\/20/g, replace: 'border-stone-300' },
    { search: /bg-primary\/10/g, replace: 'bg-stone-100' },
    { search: /text-primary/g, replace: 'text-stone-900' },
    { search: /text-slate-900/g, replace: 'text-stone-900' },
    { search: /text-slate-500/g, replace: 'text-stone-500' },
    { search: /text-slate-700/g, replace: 'text-stone-700' },
    { search: /text-slate-600/g, replace: 'text-stone-600' },
    { search: /border-slate-200/g, replace: 'border-stone-200' },
    { search: /text-slate-400/g, replace: 'text-stone-400' },
    { search: /bg-slate-100/g, replace: 'bg-stone-100' },
    { search: /bg-primary\/60/g, replace: 'bg-stone-400' },
]);

// 5. RecommendationCard.jsx
processFile('d:/ML-PROJECT-SEM-5/frontend/src/components/results/RecommendationCard.jsx', [
    { search: /border-slate-200/g, replace: 'border-stone-200' },
    { search: /bg-primary\/10/g, replace: 'bg-stone-100' },
    { search: /text-primary/g, replace: 'text-stone-900' },
    { search: /text-slate-900/g, replace: 'text-stone-900' },
    { search: /text-slate-500/g, replace: 'text-stone-500' },
]);

// 6. PredictionInsights.jsx
processFile('d:/ML-PROJECT-SEM-5/frontend/src/components/results/PredictionInsights.jsx', [
    { search: /text-amber-500/g, replace: 'text-stone-500' },
    { search: /text-slate-900/g, replace: 'text-stone-900' },
    { search: /border-slate-200/g, replace: 'border-stone-200' },
    { search: /bg-primary\/10/g, replace: 'bg-stone-100' },
    { search: /text-primary/g, replace: 'text-stone-900' },
    { search: /text-slate-700/g, replace: 'text-stone-700' },
]);

// 7. StrengthCard.jsx
processFile('d:/ML-PROJECT-SEM-5/frontend/src/components/results/StrengthCard.jsx', [
    { search: /bg-emerald-50/g, replace: 'bg-stone-50' },
    { search: /text-emerald-700/g, replace: 'text-stone-900' },
    { search: /border-emerald-200/g, replace: 'border-stone-200' },
    { search: /icon: '🌟'/g, replace: 'icon: "✦"' },
    { search: /bg-blue-50/g, replace: 'bg-stone-50' },
    { search: /text-blue-700/g, replace: 'text-stone-900' },
    { search: /border-blue-200/g, replace: 'border-stone-200' },
    { search: /icon: '💪'/g, replace: 'icon: "✧"' },
    { search: /bg-amber-50/g, replace: 'bg-stone-50' },
    { search: /text-amber-700/g, replace: 'text-stone-900' },
    { search: /border-amber-200/g, replace: 'border-stone-200' },
    { search: /icon: '✅'/g, replace: 'icon: "⋆"' },
    { search: /text-amber-500/g, replace: 'text-stone-500' },
    { search: /text-slate-900/g, replace: 'text-stone-900' },
    { search: /text-slate-700/g, replace: 'text-stone-700' },
]);

// 8. PredictionFacts.jsx
processFile('d:/ML-PROJECT-SEM-5/frontend/src/components/results/PredictionFacts.jsx', [
    { search: /text-slate-400/g, replace: 'text-stone-400' },
    { search: /text-slate-900/g, replace: 'text-stone-900' },
    { search: /border-slate-200/g, replace: 'border-stone-200' },
    { search: /divide-slate-100/g, replace: 'divide-stone-100' },
    { search: /text-slate-500/g, replace: 'text-stone-500' },
]);

// 9. AssessmentRecap.jsx
processFile('d:/ML-PROJECT-SEM-5/frontend/src/components/results/AssessmentRecap.jsx', [
    { search: /text-slate-500/g, replace: 'text-stone-500' },
    { search: /text-slate-900/g, replace: 'text-stone-900' },
    { search: /text-slate-400/g, replace: 'text-stone-400' },
    { search: /border-slate-200/g, replace: 'border-stone-200' },
    { search: /divide-slate-100/g, replace: 'divide-stone-100' },
]);

// 10. EmptyState.jsx
processFile('d:/ML-PROJECT-SEM-5/frontend/src/components/results/EmptyState.jsx', [
    { search: /bg-slate-100/g, replace: 'bg-stone-100' },
    { search: /text-slate-400/g, replace: 'text-stone-400' },
    { search: /text-slate-900/g, replace: 'text-stone-900' },
    { search: /text-slate-500/g, replace: 'text-stone-500' },
]);

// 11. LoadingState.jsx
processFile('d:/ML-PROJECT-SEM-5/frontend/src/components/results/LoadingState.jsx', [
    { search: /bg-slate-200/g, replace: 'bg-stone-200' },
    { search: /border-slate-200/g, replace: 'border-stone-200' },
]);

// 12. ResultSummary.jsx
processFile('d:/ML-PROJECT-SEM-5/frontend/src/components/results/ResultSummary.jsx', [
    { search: /text-amber-500/g, replace: 'text-stone-500' },
    { search: /text-slate-900/g, replace: 'text-stone-900' },
    { search: /border-slate-200/g, replace: 'border-stone-200' },
    { search: /text-slate-600/g, replace: 'text-stone-600' },
    { search: /bg-slate-100/g, replace: 'bg-stone-100' },
    { search: /text-slate-500/g, replace: 'text-stone-500' },
]);

console.log('Done replacement script');

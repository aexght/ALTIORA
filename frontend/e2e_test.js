const { chromium } = require('playwright');
const fs = require('fs');
const pdfParse = require('pdf-parse');

async function delay(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }

async function runAssessment(page, profile) {
  await page.goto('http://localhost:5173/');
  await page.click('text="Take the Free Assessment"');
  
  // Student Form
  await page.fill('input[name="name"]', profile.name);
  await page.fill('input[name="age"]', '17');
  await page.selectOption('select', { index: 1 });
  await page.selectOption('select', { index: 1 });
  await page.click('button:has-text("Continue")');
  
  // Academic Form
  await page.selectOption('select', profile.stream);
  await page.fill('input[type="number"]', '85'); // Class 10
  
  // Subjects
  if (profile.stream === 'Science') {
    const inputs = await page.$$('input[type="number"]');
    // inputs[0] is class10
    // the rest are subjects
    const subjects = ['Physics_Marks', 'Chemistry_Marks', 'Maths_Marks', 'Biology_Marks', 'English_Marks', 'Computer_Science_Marks'];
    for (let i = 0; i < profile.marks.length; i++) {
       if (inputs[i+1] && profile.marks[i] !== null) {
          await inputs[i+1].fill(profile.marks[i].toString());
       }
    }
  } else if (profile.stream === 'Commerce') {
    const inputs = await page.$$('input[type="number"]');
    for (let i = 0; i < profile.marks.length; i++) {
       if (inputs[i+1] && profile.marks[i] !== null) {
          await inputs[i+1].fill(profile.marks[i].toString());
       }
    }
  }

  await page.click('button:has-text("Continue")');
  
  // Questionnaire length
  await page.click('button:has-text("10 Questions")');
  await page.click('button:has-text("Start")');
  
  // Assessment
  for (let i = 0; i < 10; i++) {
    await delay(100);
    const options = await page.$$('.space-y-3 button');
    if (options.length > 0) {
      await options[0].click();
      await delay(100);
    }
  }

  await page.waitForSelector('text="View Results"', { timeout: 10000 });
  await page.click('button:has-text("View Results")');
  await page.waitForSelector('text="Your Predicted Career Domain"', { timeout: 10000 });
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ acceptDownloads: true });
  const page = await context.newPage();

  // Test 1: Science
  console.log("=== Test 1: Science Student ===");
  await runAssessment(page, {
    name: 'Science Student',
    stream: 'Science',
    marks: [85, 85, 85, 85, 85, null] // Phys, Chem, Math, Bio, Eng
  });
  
  let heroText = await page.textContent('.flex.items-center.justify-center.gap-3.flex-wrap');
  console.log("Hero Text:", heroText);
  if (heroText.includes('00%') || heroText.includes('0.0%')) console.error("ERROR: Suspicious percentage found in Hero!");

  // Test 2: Exact failure case
  console.log("\n=== Test 2: Failure Case Regression ===");
  await runAssessment(page, {
    name: 'Failure Case',
    stream: 'Science',
    // Physics: 90, Chemistry: 89, Maths: 87, Bio: 100, Eng: 90
    marks: [90, 89, 87, 100, 90, null]
  });
  
  heroText = await page.textContent('.flex.items-center.justify-center.gap-3.flex-wrap');
  console.log("Hero Text (Test 2):", heroText);
  if (heroText.includes('00%') || heroText.includes('0.0%')) console.error("ERROR: Suspicious percentage found in Hero!");

  // Test 3: Commerce elective
  console.log("\n=== Test 3: Commerce Elective Regression ===");
  await runAssessment(page, {
    name: 'Commerce Student',
    stream: 'Commerce',
    // Accountancy: 98, Business: 85, Economics: 85, English: 85, Math: null, CS: 100
    marks: [98, 85, 85, 85, null, 100]
  });

  const whyText = await page.textContent('section[aria-labelledby="why-heading"]');
  console.log("Why This Recommendation Text contains 'Computer Science':", whyText.includes('Computer Science'));
  if (!whyText.includes('Computer Science')) console.error("ERROR: Computer Science elective lost from reasoning!");

  // Test 4: PDF Generation
  console.log("\n=== Test 4: Generate Actual PDF ===");
  const [download] = await Promise.all([
    page.waitForEvent('download'),
    page.click('button:has-text("Download Career Report")')
  ]);
  const path = await download.path();
  console.log("PDF downloaded to", path);
  
  let dataBuffer = fs.readFileSync(path);
  let pdfData = await pdfParse(dataBuffer);
  
  console.log("\n=== PDF Content Analysis ===");
  const text = pdfData.text;
  if (text.includes('00%') || text.includes('0.0%')) {
     console.error("ERROR: Found excessive percentage scaling in PDF text!");
     const matches = text.match(/.{0,20}\d{3,}%.{0,20}/g);
     if (matches) console.log("Problematic strings:", matches);
  } else {
     console.log("PDF percentages are sensible.");
  }

  if (text.includes("How your recommendation was created")) {
     console.log("PDF contains updated methodology text.");
  } else {
     console.error("PDF methodology text NOT found.");
  }
  
  if (text.includes('Computer Science')) {
     console.log("Computer Science correctly propagated to PDF.");
  } else {
     console.error("Computer Science NOT found in PDF.");
  }

  await browser.close();
  console.log("Tests completed.");
})();

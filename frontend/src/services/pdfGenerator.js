import { jsPDF } from 'jspdf';
import { formatPercent } from '../utils/formatters';

// ---------------------------------------------------------------------------
// Static course descriptions — honest, verified, student-facing
// ---------------------------------------------------------------------------
const COURSE_INFO_MAP = {
  'B.Tech Computer Science': {
    what: 'A four-year engineering degree covering algorithms, software development, data structures, operating systems, and system design.',
    leads: 'Software engineering, data science, web and mobile development, cybersecurity, and IT consulting.',
    consider: 'Explore whether you enjoy logical problem-solving, programming, and applied mathematics.',
  },
  'B.Tech Computer Science and Engineering': {
    what: 'A four-year engineering programme combining computer science theory with practical software and hardware engineering skills.',
    leads: 'Software development, systems engineering, embedded systems, AI/ML engineering, and IT infrastructure.',
    consider: 'Strong background in mathematics and a genuine interest in computing will help you thrive.',
  },
  'B.Tech Information Technology': {
    what: 'A four-year degree focused on the practical application of computing — including networks, databases, and enterprise software.',
    leads: 'IT management, network administration, database development, and enterprise systems.',
    consider: 'A good fit if you are more interested in applying technology to real-world problems than in theoretical computing.',
  },
  'B.Tech Mechanical Engineering': {
    what: 'A four-year engineering degree focused on mechanics, machines, manufacturing, thermodynamics, and engineering design.',
    leads: 'Mechanical design, manufacturing, automotive engineering, aerospace, and production engineering.',
    consider: 'Explore whether you enjoy physics, mathematics, mechanical systems, and hands-on engineering problems.',
  },
  'B.Tech Civil Engineering': {
    what: 'A four-year degree covering the design, construction, and maintenance of infrastructure — roads, bridges, dams, and buildings.',
    leads: 'Structural engineering, construction management, urban planning, and environmental engineering.',
    consider: 'A good fit if you enjoy large-scale physical projects and have strong spatial reasoning.',
  },
  'B.Tech Electrical Engineering': {
    what: 'A four-year degree dealing with electricity, electronics, electromagnetism, and control systems.',
    leads: 'Power systems, electronics design, control engineering, and telecommunications.',
    consider: 'Requires strong aptitude in physics and mathematics — particularly calculus and electromagnetism.',
  },
  'B.Tech Electronics and Communication': {
    what: 'A four-year degree combining electronics with signal processing, communication networks, and embedded systems.',
    leads: 'Telecommunications, VLSI design, embedded systems, and electronics research.',
    consider: 'A good match if you are interested in both the hardware and communication aspects of technology.',
  },
  'B.Tech Chemical Engineering': {
    what: 'A four-year degree applying chemistry and engineering principles to design processes for chemicals, materials, and energy.',
    leads: 'Chemical manufacturing, petroleum engineering, pharmaceuticals, and process design.',
    consider: 'Requires a strong foundation in chemistry, physics, and mathematics.',
  },
  'B.Sc Computer Science': {
    what: 'A three-year science degree covering programming, computing concepts, data structures, and software systems.',
    leads: 'Software development, database administration, system analysis, and IT support.',
    consider: 'A strong alternative to B.Tech if you prefer a shorter programme focused on computing principles.',
  },
  'BCA (Bachelor of Computer Applications)': {
    what: 'A three-year degree focused on practical software development, web design, and computing applications.',
    leads: 'Application development, web design, IT infrastructure, and software testing.',
    consider: 'More application-focused than B.Sc CS; less emphasis on theoretical mathematics.',
  },
  'B.Sc Mathematics': {
    what: 'A three-year degree in pure and applied mathematics — algebra, calculus, statistics, and mathematical modelling.',
    leads: 'Data analysis, actuarial science, statistics, quantitative research, and further academic study.',
    consider: 'Requires abstract thinking and a genuine interest in complex problem-solving.',
  },
  'B.Sc Physics': {
    what: 'A three-year degree covering classical mechanics, electrodynamics, quantum theory, and experimental physics.',
    leads: 'Research, academia, data analysis, aerospace, and technical consulting.',
    consider: 'Well-suited to students who enjoy understanding natural phenomena through experimentation and mathematics.',
  },
  'B.Sc Chemistry': {
    what: 'A three-year degree studying the composition, structure, and properties of matter and chemical reactions.',
    leads: 'Pharmaceuticals, chemical manufacturing, environmental science, and research.',
    consider: 'Requires precision, comfort with laboratory work, and strong analytical skills.',
  },
  'B.Sc Biology': {
    what: 'A three-year degree covering the principles of life — cell biology, genetics, ecology, and physiology.',
    leads: 'Biomedical research, environmental science, agriculture, and healthcare support roles.',
    consider: 'Well-matched if you enjoy the life sciences and are comfortable with laboratory-based learning.',
  },
  'MBBS': {
    what: 'A five-and-a-half year undergraduate medical degree combining classroom learning with clinical training.',
    leads: 'Medical practice across all specialities — from general medicine to surgery, psychiatry, and research.',
    consider: 'Requires a deep long-term commitment. Admission is highly competitive and requires strong Biology and Chemistry.',
  },
  'B.Pharm (Bachelor of Pharmacy)': {
    what: 'A four-year degree covering pharmaceutical sciences — drug development, pharmacology, and medicine dispensing.',
    leads: 'Pharmaceutical manufacturing, drug research, hospital pharmacy, and regulatory affairs.',
    consider: 'A strong foundation in Chemistry and Biology is important for this programme.',
  },
  'B.Com (General)': {
    what: 'A three-year undergraduate degree covering accounting, finance, taxation, and business management.',
    leads: 'Accounting, banking, financial analysis, corporate administration, and business management.',
    consider: 'A good fit if you have an aptitude for numbers, financial records, and business organization.',
  },
  'B.Com (Honours)': {
    what: 'A specialized three-year degree providing in-depth study of commerce, accounting, and financial theory.',
    leads: 'Chartered accountancy, company secretaryship, financial consulting, and advanced business roles.',
    consider: 'Requires strong quantitative skills and interest in complex financial and economic concepts.',
  },
  'B.B.A': {
    what: 'A three-year degree focused on business administration, management principles, and organizational strategy.',
    leads: 'Business management, marketing, human resources, sales, and entrepreneurship.',
    consider: 'Evaluate your interest in leadership, strategy, communication, and teamwork.',
  },
  'B.A Economics': {
    what: 'A three-year degree studying the production, distribution, and consumption of goods and services.',
    leads: 'Economic research, financial forecasting, policy analysis, and banking.',
    consider: 'Combines mathematical aptitude with an interest in social systems and human behaviour.',
  },
};

const getCourseInfo = (courseName) => {
  if (!courseName) return null;
  if (COURSE_INFO_MAP[courseName]) return COURSE_INFO_MAP[courseName];
  const match = Object.keys(COURSE_INFO_MAP).find(
    k => courseName.toLowerCase().includes(k.toLowerCase()) || k.toLowerCase().includes(courseName.toLowerCase())
  );
  return match ? COURSE_INFO_MAP[match] : null;
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
const sanitizeFilename = (name) => {
  if (!name) return 'student';
  return name.replace(/[^a-z0-9]/gi, '_').toLowerCase();
};

const safeStr = (val, fallback = 'N/A') =>
  (val !== null && val !== undefined && String(val).trim() !== '') ? String(val).trim() : fallback;

// ---------------------------------------------------------------------------
// Main PDF generator
// ---------------------------------------------------------------------------
export const generateCareerReportPDF = async (state) => {
  return new Promise((resolve, reject) => {
    try {
      const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });

      const { student, academic, prediction: predictionData } = state;
      const {
        prediction = {},
        top_domains = [],
        recommended_courses = [],
        recommended_colleges = [],
        assessment_profile = [],
        reasoning = {},
      } = predictionData || {};

      const PAGE_W  = doc.internal.pageSize.getWidth();   // 210 mm
      const PAGE_H  = doc.internal.pageSize.getHeight();  // 297 mm

      // ── Design tokens ─────────────────────────────────────────────────────
      const MARGIN      = 20;          // left / right text margin
      const CONTENT_W   = PAGE_W - MARGIN * 2;  // 170 mm usable width
      const BORDER_INSET = 8;          // page-border distance from paper edge
      const FOOTER_Y     = PAGE_H - 10; // footer baseline

      let y = MARGIN;

      // Monochrome palette — warm charcoal + stone greys
      const C = {
        ink:     [20, 18, 16],    // near-black headings
        body:    [62, 58, 54],    // dark stone — body text
        muted:   [120, 115, 108], // mid-stone — supporting labels / captions
        rule:    [210, 207, 202], // light rule lines
        track:   [232, 229, 225], // bar-chart empty track
        border:  [188, 185, 180], // page border — subtle, 1-shade darker than rule
        fill:    [246, 245, 242], // off-white area fills
      };

      // ── Page border (drawn on every page after content, in the footer pass) ─
      const drawPageBorder = () => {
        doc.setDrawColor(...C.border);
        doc.setLineWidth(0.35);
        doc.rect(
          BORDER_INSET,
          BORDER_INSET,
          PAGE_W - BORDER_INSET * 2,
          PAGE_H - BORDER_INSET * 2
        );
      };

      // ── Core layout helpers ───────────────────────────────────────────────

      /** Guard: add a page if `needed` mm won't fit before the footer zone. */
      const needPage = (needed = 20) => {
        if (y + needed > FOOTER_Y - 12) {
          doc.addPage();
          y = MARGIN;
          return true;
        }
        return false;
      };

      /** Thin horizontal rule at current y, then advance y. */
      const rule = (color = C.rule, weight = 0.25) => {
        doc.setDrawColor(...color);
        doc.setLineWidth(weight);
        doc.line(MARGIN, y, PAGE_W - MARGIN, y);
        y += 5;
      };

      /**
       * Render wrapped text at current y.
       * lineHeight default = 5.8 mm → comfortable reading rhythm.
       */
      const text = (str, opts = {}) => {
        if (!str) return;
        const {
          size = 10, style = 'normal', color = C.body,
          indent = 0, lineHeight = 5.8, maxW,
        } = opts;
        doc.setFont('helvetica', style);
        doc.setFontSize(size);
        doc.setTextColor(...color);
        const lines = doc.splitTextToSize(str, maxW || (CONTENT_W - indent));
        const blockH = lines.length * lineHeight;
        needPage(blockH + 6);
        doc.text(lines, MARGIN + indent, y);
        y += blockH;
      };

      /**
       * Two-line section heading:
       *   SECTION N          ← small-caps label, muted
       *   Title text         ← medium bold, ink
       * Followed by a hairline rule.
       */
      const sectionHeading = (sectionLabel, title) => {
        needPage(28);
        y += 6;

        // Section number label — small, tracked, muted
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(7.5);
        doc.setTextColor(...C.muted);
        doc.text(sectionLabel.toUpperCase(), MARGIN, y);
        y += 5;

        // Section title — medium bold, ink
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(13);
        doc.setTextColor(...C.ink);
        doc.text(title, MARGIN, y);
        y += 5;

        rule(C.ink, 0.5);
      };

      /**
       * Key–value label row.
       * Label column is fixed at 38 mm so values align vertically.
       */
      const label = (lbl, val, indent = 0) => {
        if (!val || val === 'N/A') return;
        needPage(7);
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(9.5);
        doc.setTextColor(...C.muted);
        doc.text(lbl, MARGIN + indent, y);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(...C.ink);
        doc.text(String(val), MARGIN + indent + 38, y);
        y += 6.5;
      };

      /** Body paragraph: 2 mm leading, body text, 2 mm trailing. */
      const paragraph = (str, opts = {}) => {
        if (!str) return;
        y += 2;
        text(str, { size: 10, color: C.body, lineHeight: 5.8, ...opts });
        y += 3;
      };

      /**
       * Horizontal bar chart.
       * LABEL_W   = fixed label column (left-aligned subject names).
       * BAR_W     = fixed bar column.
       * PCT_W     = fixed percentage label column (right-aligned, always aligned).
       */
      const barChart = (items, valueKey = 'value', labelKey = 'label') => {
        if (!items || items.length === 0) return;

        const BAR_H   = 4.5;
        const ROW_GAP = 9;
        const LABEL_W = 54;   // fixed: subject name column
        const PCT_W   = 14;   // fixed: percentage column
        const BAR_W   = CONTENT_W - LABEL_W - PCT_W - 4; // remaining space → bar

        items.forEach((item) => {
          needPage(ROW_GAP + 4);
          const val      = Math.min(100, Math.max(0, Number(item[valueKey]) || 0));
          const lbl      = String(item[labelKey] || '');
          const shortLbl = lbl.length > 30 ? lbl.substring(0, 28) + '\u2026' : lbl;

          // Label — left-aligned, body grey
          doc.setFont('helvetica', 'normal');
          doc.setFontSize(8.5);
          doc.setTextColor(...C.body);
          doc.text(shortLbl, MARGIN, y + BAR_H);

          // Empty track
          doc.setFillColor(...C.track);
          doc.rect(MARGIN + LABEL_W, y + 0.5, BAR_W, BAR_H, 'F');

          // Filled bar
          if (val > 0) {
            doc.setFillColor(...C.ink);
            doc.rect(MARGIN + LABEL_W, y + 0.5, (val / 100) * BAR_W, BAR_H, 'F');
          }

          // Percentage — right-aligned in fixed column
          const pctStr = formatPercent(val);
          doc.setFontSize(8.5);
          doc.setTextColor(...C.muted);
          const pctX = MARGIN + LABEL_W + BAR_W + 3;
          doc.text(pctStr, pctX, y + BAR_H);

          y += ROW_GAP;
        });
      };

      // ══════════════════════════════════════════════════════════════════════
      // PAGE 1: COVER
      // ══════════════════════════════════════════════════════════════════════

      // ── Top rule ──
      doc.setDrawColor(...C.border);
      doc.setLineWidth(0.4);
      doc.line(MARGIN, 24, PAGE_W - MARGIN, 24);

      // ── ALTIORA wordmark ──
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(54);
      doc.setTextColor(...C.ink);
      doc.text('ALTIORA', MARGIN, 72);

      // ── Report title ──
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(13);
      doc.setTextColor(...C.muted);
      doc.text('Personal Career Guidance Report', MARGIN, 83);

      // ── Divider ──
      doc.setDrawColor(...C.rule);
      doc.setLineWidth(0.3);
      doc.line(MARGIN, 92, PAGE_W - MARGIN, 92);

      // ── Student info block ──
      const INFO_LABEL_X = MARGIN;
      const INFO_VALUE_X = MARGIN + 38;
      const INFO_SIZE    = 10.5;

      const coverRow = (lbl, val, rowY) => {
        if (!val || val === 'N/A') return;
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(INFO_SIZE);
        doc.setTextColor(...C.muted);
        doc.text(lbl, INFO_LABEL_X, rowY);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(...C.ink);
        doc.text(String(val), INFO_VALUE_X, rowY);
      };

      coverRow('Student',  safeStr(student?.name, 'Student'), 106);
      coverRow('Stream',   safeStr(academic?.stream),          116);
      coverRow('Date',     new Date().toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' }), 126);

      // ── Second divider ──
      doc.setDrawColor(...C.rule);
      doc.setLineWidth(0.3);
      doc.line(MARGIN, 136, PAGE_W - MARGIN, 136);

      // ── Subtitle ──
      doc.setFont('helvetica', 'italic');
      doc.setFontSize(9.5);
      doc.setTextColor(...C.muted);
      doc.text(
        'A personalized guide to understanding your strengths, career directions, recommended courses, and college options.',
        MARGIN, 146,
        { maxWidth: CONTENT_W }
      );

      // Cover disclaimer (bottom of page 1)
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(7.5);
      doc.setTextColor(...C.border);
      doc.text(
        'This report is for guidance purposes only. Results depend on the information supplied during assessment.',
        MARGIN, PAGE_H - 14, { maxWidth: CONTENT_W }
      );

      // ══════════════════════════════════════════════════════════════════════
      // PAGE 2: PROFILE + ACADEMIC STRENGTHS
      // ══════════════════════════════════════════════════════════════════════
      doc.addPage();
      y = MARGIN;

      sectionHeading('Section 1', 'Your Profile');
      label('Name',     safeStr(student?.name));
      label('Age',      safeStr(student?.age));
      const loc = [student?.district, student?.state].filter(Boolean).join(', ');
      label('Location', safeStr(loc));
      label('Stream',   safeStr(academic?.stream));
      label('Class 10', academic?.class10Percentage ? `${academic.class10Percentage}%` : null);

      const subjectMarks = academic?.subjectMarks || {};
      const validMarks = Object.entries(subjectMarks)
        .filter(([, v]) => v !== '' && v !== null && v !== undefined && !isNaN(Number(v)) && Number(v) > 0)
        .map(([, v]) => Number(v));
      if (validMarks.length > 0) {
        const avg12 = (validMarks.reduce((s, v) => s + v, 0) / validMarks.length).toFixed(1);
        label('Class 12', `${avg12}%`);
      }
      y += 4;

      sectionHeading('Section 2', 'Your Academic Strengths');

      const academicChartData = Object.entries(subjectMarks)
        .filter(([, v]) => v !== '' && v !== null && v !== undefined && !isNaN(Number(v)) && Number(v) > 0)
        .map(([k, v]) => ({
          label: k.replace(/_Marks$/, '').replace(/([A-Z])/g, ' $1').trim(),
          value: Number(v),
          key: k,
        }))
        .sort((a, b) => b.value - a.value);

      if (academicChartData.length > 0) {
        barChart(academicChartData);
        y += 3;
        const top = academicChartData[0];
        paragraph(
          `Your strongest academic signal is ${top.label} (${top.value}%). ` +
          (academicChartData.length > 1
            ? `This is followed by ${academicChartData.slice(1, 3).map(x => `${x.label} (${x.value}%)`).join(' and ')}.`
            : '')
        );
      } else {
        paragraph('Academic marks were not provided or could not be parsed.');
      }

      // ══════════════════════════════════════════════════════════════════════
      // SECTION 3: ASSESSMENT PROFILE
      // ══════════════════════════════════════════════════════════════════════
      const meaningfulTraits = assessment_profile.filter(t => t.value > 0);

      if (meaningfulTraits.length > 0) {
        sectionHeading('Section 3', 'Your Assessment Profile');
        paragraph(
          'Based on your questionnaire responses, the following tendencies were identified. ' +
          'These reflect patterns in your answers — they are descriptive, not diagnostic.'
        );
        y += 2;

        meaningfulTraits.forEach((trait) => {
          needPage(22);

          // Trait name — bold, ink
          doc.setFont('helvetica', 'bold');
          doc.setFontSize(10);
          doc.setTextColor(...C.ink);
          doc.text(trait.label, MARGIN, y);

          // Strength · value — same baseline, muted
          doc.setFont('helvetica', 'normal');
          doc.setFontSize(9);
          doc.setTextColor(...C.muted);
          doc.text(`${trait.strength}  \u00B7  ${formatPercent(trait.value)}`, MARGIN + 58, y);
          y += 5.5;

          // Description — indented, body colour, smaller
          text(trait.description, { size: 9, color: C.body, indent: 4, lineHeight: 5.2 });
          y += 4;
        });
      }

      // ══════════════════════════════════════════════════════════════════════
      // SECTION 4: CAREER RECOMMENDATION
      // ══════════════════════════════════════════════════════════════════════
      const domainName = safeStr(prediction?.domain, 'Your Predicted Career Domain');

      sectionHeading('Section 4', 'Your Career Recommendation');

      doc.setFont('helvetica', 'bold');
      doc.setFontSize(19);
      doc.setTextColor(...C.ink);
      doc.text(domainName, MARGIN, y);
      y += 10;

      if (top_domains && top_domains.length > 0) {
        text('How your profile aligns with the supported career domains:', { size: 9, style: 'italic', color: C.muted });
        y += 5;
        barChart(top_domains.slice(0, 5).map(d => ({ label: d.domain, value: d.probability })));
        y += 2;
        paragraph(
          'These percentages represent how strongly your profile aligns with each career domain ' +
          'according to the model\'s analysis. They are probability estimates — not predictions ' +
          'of success, and not a ranking of how valuable each domain is.'
        );
      }

      // ══════════════════════════════════════════════════════════════════════
      // SECTION 5: WHY THIS RECOMMENDATION?
      // ══════════════════════════════════════════════════════════════════════
      sectionHeading('Section 5', 'Why This Recommendation?');

      // Reasoning summary
      if (reasoning?.summary) {
        paragraph(reasoning.summary, { color: C.ink });
      }

      // ── Academic evidence ──
      const acEvidence = reasoning?.academic_evidence || [];
      const topAcademic = acEvidence.filter(e => e.value >= 65);
      if (topAcademic.length > 0) {
        y += 5;
        text('Academic evidence', { size: 9.5, style: 'bold', color: C.ink });
        y += 1;
        doc.setDrawColor(...C.rule);
        doc.setLineWidth(0.2);
        doc.line(MARGIN, y, PAGE_W - MARGIN, y);
        y += 5;

        topAcademic.forEach(ev => {
          needPage(8);
          const strength = ev.value >= 80 ? 'Excellent' : ev.value >= 65 ? 'Strong' : 'Good';
          doc.setFont('helvetica', 'normal');
          doc.setFontSize(9.5);
          doc.setTextColor(...C.body);
          doc.text('\u2022', MARGIN + 4, y);
          doc.setTextColor(...C.ink);
          doc.text(ev.label, MARGIN + 10, y);
          doc.setTextColor(...C.muted);
          doc.text(`${strength} (${ev.value}%)`, MARGIN + 60, y);
          y += 6;
        });
      }

      // ── Assessment evidence ──
      const topAssessment = meaningfulTraits.filter(t => t.value >= 60);
      if (topAssessment.length > 0) {
        y += 5;
        text('Assessment evidence', { size: 9.5, style: 'bold', color: C.ink });
        y += 1;
        doc.setDrawColor(...C.rule);
        doc.setLineWidth(0.2);
        doc.line(MARGIN, y, PAGE_W - MARGIN, y);
        y += 5;

        topAssessment.slice(0, 4).forEach(t => {
          needPage(8);
          doc.setFont('helvetica', 'normal');
          doc.setFontSize(9.5);
          doc.setTextColor(...C.body);
          doc.text('\u2022', MARGIN + 4, y);
          doc.setTextColor(...C.ink);
          doc.text(t.label, MARGIN + 10, y);
          doc.setTextColor(...C.muted);
          doc.text(t.strength, MARGIN + 60, y);
          y += 6;
        });
      }

      // ── Important note ──
      y += 5;
      text('Important note', { size: 9.5, style: 'bold', color: C.ink });
      y += 1;
      doc.setDrawColor(...C.rule);
      doc.setLineWidth(0.2);
      doc.line(MARGIN, y, PAGE_W - MARGIN, y);
      y += 4;
      paragraph(
        'The ALTIORA model evaluates your full profile — both academic and assessment dimensions — ' +
        'simultaneously. The recommendation reflects the overall pattern of signals, not the strongest ' +
        'single mark or questionnaire response. No individual feature alone determines the outcome.'
      );

      // ══════════════════════════════════════════════════════════════════════
      // SECTION 6: RECOMMENDED COURSES
      // ══════════════════════════════════════════════════════════════════════
      needPage(30);
      sectionHeading('Section 6', 'Your Recommended Courses');

      if (recommended_courses && recommended_courses.length > 0) {
        recommended_courses.forEach((course, idx) => {
          const courseName = course.course || 'Unknown Course';
          const info = getCourseInfo(courseName);

          needPage(54);

          // Course number + name
          doc.setFont('helvetica', 'bold');
          doc.setFontSize(11.5);
          doc.setTextColor(...C.ink);
          doc.text(`${idx + 1}.  ${courseName}`, MARGIN, y);
          y += 7;

          const courseSubLabel = (lbl) => {
            text(lbl, { size: 8.5, style: 'bold', color: C.ink, indent: 7 });
            y += 1;
          };
          const coursePara = (str) => {
            text(str, { size: 9, color: C.body, indent: 7, lineHeight: 5.4 });
            y += 3;
          };

          if (info) {
            courseSubLabel('What is it?');
            coursePara(info.what);

            courseSubLabel('Why ALTIORA suggested it');
            coursePara(
              `This course belongs to the ${domainName} domain — your strongest predicted career direction. ` +
              (reasoning?.academic_pattern ? reasoning.academic_pattern + ' ' : '') +
              'The course was selected because it offers a relevant pathway within this domain.'
            );

            courseSubLabel('Where it can lead');
            coursePara(info.leads);

            courseSubLabel('Before choosing it');
            coursePara(info.consider);
          } else {
            coursePara(
              `This course is associated with the ${domainName} domain. ` +
              'Please research the full curriculum and admission requirements before applying.'
            );
          }

          y += 4;
          if (idx < recommended_courses.length - 1) {
            needPage(6);
            doc.setDrawColor(...C.rule);
            doc.setLineWidth(0.2);
            doc.line(MARGIN, y - 1, PAGE_W - MARGIN, y - 1);
            y += 3;
          }
        });
      } else {
        paragraph('No specific courses are available for this recommendation at this time.');
      }

      // ══════════════════════════════════════════════════════════════════════
      // SECTION 7: RECOMMENDED COLLEGES
      // ══════════════════════════════════════════════════════════════════════
      needPage(30);
      sectionHeading('Section 7', 'Recommended Colleges');
      paragraph(
        'The following institutions offer the recommended course and are included in ' +
        "ALTIORA's verified college dataset. This list reflects course availability, not a " +
        "ranking of the college's quality, prestige, or suitability for you personally. " +
        'Always verify current fees, admission criteria, and course availability through ' +
        'official institutional sources before applying.'
      );
      y += 3;

      if (recommended_colleges && recommended_colleges.length > 0) {
        const COL_LBL_X  = MARGIN + 8;     // label indent
        const COL_VAL_X  = MARGIN + 30;    // value column — fixed
        recommended_colleges.forEach((c, idx) => {
          needPage(32);
          const collegeName = safeStr(c.college_name);
          const locParts    = [c.district, c.state].filter(Boolean);
          const collegeLoc  = locParts.join(', ') || (c.area || '');

          // College name — bold, ink
          doc.setFont('helvetica', 'bold');
          doc.setFontSize(10);
          doc.setTextColor(...C.ink);
          doc.text(`${idx + 1}.  ${collegeName}`, MARGIN, y);
          y += 6;

          // Detail rows — muted label, body value
          const collegeRow = (lbl, val) => {
            if (!val || val === 'Not Verified') return;
            doc.setFont('helvetica', 'normal');
            doc.setFontSize(9);
            doc.setTextColor(...C.muted);
            doc.text(lbl, COL_LBL_X, y);
            doc.setTextColor(...C.body);
            const valLines = doc.splitTextToSize(String(val), CONTENT_W - COL_VAL_X + MARGIN);
            doc.text(valLines, COL_VAL_X, y);
            y += Math.max(valLines.length * 5, 5.5);
          };

          collegeRow('Course',   c.course);
          collegeRow('Location', collegeLoc);
          collegeRow('Type',     c.ownership);
          collegeRow('NAAC',     c.naac);

          y += 4;
          if (idx < recommended_colleges.length - 1) {
            doc.setDrawColor(...C.rule);
            doc.setLineWidth(0.2);
            doc.line(MARGIN, y - 1, PAGE_W - MARGIN, y - 1);
            y += 3;
          }
        });
      } else {
        paragraph('No colleges matched the recommended course and location criteria. Try adjusting your location preferences.');
      }

      // ══════════════════════════════════════════════════════════════════════
      // SECTION 8: HOW ALTIORA WORKS
      // ══════════════════════════════════════════════════════════════════════
      needPage(40);
      sectionHeading('Section 8', 'How ALTIORA Works');

      const methodology = [
        ['1. Student Profile', 'ALTIORA collects your academic stream, subject performance across core and elective subjects, Class 10 and Class 12 percentages, and your location.'],
        ['2. Assessment', 'You complete a structured questionnaire designed to measure eight dimensions: Logical Reasoning, Analytical Thinking, Technical Interest, Business Interest, Creative Thinking, Communication, Leadership Orientation, and Research Orientation. Each dimension is scored from 0\u2013100 based on your actual responses.'],
        ['3. Feature Preparation', 'Your academic data and assessment scores are converted into a consistent numerical format that the machine-learning model can evaluate. This ensures every student is assessed on the same objective basis.'],
        ['4. Career Domain Prediction', 'The features are passed to a Random Forest classifier \u2014 a model that consists of many individual decision trees. Each tree independently evaluates the profile through different learned decision patterns. The trees\u2019 outputs are then aggregated to produce a final prediction. This is important: the recommendation is not determined by any single subject mark or questionnaire answer, but by the combined signal across all features.'],
        ['5. Domain Probabilities', 'The model produces probability estimates for each supported career domain. The domain with the highest probability becomes the primary recommendation. These probabilities reflect the model\u2019s degree of alignment \u2014 they are not a percentage chance that you will succeed in that career.'],
        ['6. Course Selection', 'Once the career domain is identified, ALTIORA selects courses associated with that domain, taking course availability and relevance into account.'],
        ['7. College Matching', 'Finally, ALTIORA checks a verified college dataset to identify institutions that explicitly offer the recommended course. Only colleges with confirmed course availability appear in the report. This makes the college list a course-availability match \u2014 not a claim about which institution is objectively best for you.'],
      ];

      methodology.forEach(([heading, body]) => {
        needPage(28);
        text(heading, { size: 10, style: 'bold', color: C.ink });
        y += 1;
        paragraph(body);
        y += 1;
      });

      // ══════════════════════════════════════════════════════════════════════
      // SECTION 9: YOUR NEXT STEPS
      // ══════════════════════════════════════════════════════════════════════
      needPage(50);
      sectionHeading('Section 9', 'Your Next Steps');

      const steps = [
        ['Compare the recommended courses', `Review each course in this report and research what students actually study, what the workload involves, and what the entry requirements are for the institutions you are considering.`],
        ['Test your interest', `Try a beginner activity, online resource, or short project related to ${domainName}. Your response to hands-on exposure is a useful signal that this report cannot capture.`],
        ['Investigate colleges independently', "Check admission requirements, current fees, course availability, hostel facilities, and placement records directly through each college's official website or prospectus."],
        ['Identify skill gaps', 'Based on the recommended courses, identify two or three skills or subjects that would strengthen your preparation. Consider how you might develop these before applying.'],
        ['Make the final decision yourself', 'Use ALTIORA as one input among many \u2014 alongside your own interests, goals, family circumstances, and advice from teachers, counselors, and professionals in the field.'],
      ];

      steps.forEach(([heading, body], idx) => {
        needPage(22);
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(10);
        doc.setTextColor(...C.ink);
        doc.text(`${idx + 1}.  ${heading}`, MARGIN, y);
        y += 5.5;
        paragraph(body, { indent: 8 });
        y += 1;
      });

      // ══════════════════════════════════════════════════════════════════════
      // SECTION 10: LIMITATIONS & FUTURE SCOPE
      // ══════════════════════════════════════════════════════════════════════
      needPage(40);
      sectionHeading('Section 10', 'Limitations & Future Scope');

      text('Limitations', { size: 10, style: 'bold', color: C.ink });
      y += 3;
      const limitations = [
        'ALTIORA provides career guidance, not certainty. The recommendation is a data-driven signal, not a prediction of your future career or academic success.',
        'Results depend on the accuracy of the information you supplied. Incorrect or incomplete academic data will affect the recommendation.',
        'The current model is trained on Science and Commerce student profiles only. Arts and Humanities streams are not currently supported.',
        "Course and college information in ALTIORA's dataset may not reflect the most recent changes. Always verify through official sources.",
        'The Random Forest model identifies statistical patterns \u2014 it does not have access to your full personal context, interests, or circumstances.',
      ];
      limitations.forEach(lim => {
        needPage(12);
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(9.5);
        doc.setTextColor(...C.body);
        const limLines = doc.splitTextToSize(lim, CONTENT_W - 14);
        doc.text('\u2022', MARGIN + 4, y);
        doc.text(limLines, MARGIN + 10, y);
        y += limLines.length * 5.6 + 2;
      });

      y += 5;
      text('Future Scope', { size: 10, style: 'bold', color: C.ink });
      y += 2;
      paragraph(
        'Future versions of ALTIORA aim to include comprehensive support for Arts, Humanities, and Vocational streams, ' +
        'expand the verified college dataset to cover more regions and institutions, and incorporate updated ' +
        'admission and placement data. The assessment questionnaire will also be expanded to capture a broader ' +
        'range of aptitude and interest dimensions.'
      );

      // ══════════════════════════════════════════════════════════════════════
      // FOOTER + PAGE BORDER on every page
      // ══════════════════════════════════════════════════════════════════════
      const totalPages = doc.internal.getNumberOfPages();
      for (let i = 1; i <= totalPages; i++) {
        doc.setPage(i);

        // Page border — thin, neutral, inset from paper edge
        drawPageBorder();

        // Footer rule
        doc.setDrawColor(...C.rule);
        doc.setLineWidth(0.2);
        doc.line(MARGIN, FOOTER_Y - 4, PAGE_W - MARGIN, FOOTER_Y - 4);

        // Footer text
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(7.5);
        doc.setTextColor(...C.muted);
        doc.text('ALTIORA  \u00B7  Personal Career Guidance Report', MARGIN, FOOTER_Y);
        doc.text(`Page ${i} of ${totalPages}`, PAGE_W - MARGIN, FOOTER_Y, { align: 'right' });
      }

      const filename = `ALTIORA_Career_Report_${sanitizeFilename(student?.name)}.pdf`;
      doc.save(filename);
      resolve(true);
    } catch (error) {
      console.error('PDF Generation Error:', error);
      reject(error);
    }
  });
};

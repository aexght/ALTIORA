import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';

/**
 * AnimatedNumber Component
 * @param {Object} props
 * @param {number} props.value - The target number to animate to
 * @param {string} [props.suffix] - Suffix to append to the number
 * @returns {React.JSX.Element}
 */
function AnimatedNumber({ value, suffix = '' }) {
  const [display, setDisplay] = useState(0);
  const ref = useRef(null);
  const animated = useRef(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !animated.current) {
          animated.current = true;
          const duration = 1500;
          const start = performance.now();
          
          function tick(now) {
            const p = Math.min((now - start) / duration, 1);
            const eased = 1 - (1 - p) * (1 - p); // ease-out
            setDisplay(Math.floor(eased * value));
            if (p < 1) requestAnimationFrame(tick);
          }
          
          requestAnimationFrame(tick);
        }
      },
      { threshold: 0.3 }
    );
    
    observer.observe(el);
    return () => observer.disconnect();
  }, [value]);

  return <span ref={ref}>{display}{suffix}</span>;
}

/**
 * Statistics Section Component
 * @returns {React.JSX.Element}
 */
export const Statistics = () => {
  const stats = [
    { id: 1, value: 10, suffix: '', label: 'Career Domains' },
    { id: 2, value: 40, suffix: '', label: 'Assessment Questions' },
    { id: 3, value: 100, suffix: '+', label: 'Courses Mapped' },
    { id: 4, value: 120, suffix: '+', label: 'Colleges Listed' },
  ];

  return (
    <section className="py-20 lg:py-24 max-w-5xl mx-auto px-6 altiora-bg">
      <div className="text-center mb-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <h2 className="text-3xl md:text-4xl font-bold text-stone-900 mb-4 font-display">Built on Real Data</h2>
          <p className="text-lg text-stone-600 max-w-2xl mx-auto">
            Every recommendation is backed by a comprehensive dataset.
          </p>
        </motion.div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <motion.div
            key={stat.id}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: index * 0.1, duration: 0.5 }}
            className="bg-white rounded-xl border border-stone-200 p-6 text-center shadow-card"
          >
            <div className="text-3xl font-bold text-stone-900 font-display">
              <AnimatedNumber value={stat.value} suffix={stat.suffix} />
            </div>
            <p className="text-sm text-stone-600 mt-1">{stat.label}</p>
          </motion.div>
        ))}
      </div>
    </section>
  );
};

export default Statistics;

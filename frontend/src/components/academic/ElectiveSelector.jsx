/**
 * ElectiveSelector — Card-based elective subject selector.
 *
 * Renders selectable cards for each available elective in the chosen stream.
 * Enforces min 1 / max 2 elective constraint with inline validation.
 * Selected cards show a blue border + check icon.
 */

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Check, 
  Calculator, 
  Dna, 
  Terminal, 
  BarChart, 
  LineChart, 
  Landmark, 
  Globe, 
  Gavel, 
  Brain, 
  Users,
  BookOpen
} from 'lucide-react';
import FormSection from '../forms/FormSection';
import { STREAM_SUBJECTS, MAX_ELECTIVES } from '../../utils/constants';
import { cn } from '../../utils/cn';

/** Icons for known elective subjects (decorative). */
const ELECTIVE_ICONS = {
  Mathematics: Calculator,
  Biology: Dna,
  'Computer Science': Terminal,
  Statistics: BarChart,
  Economics: LineChart,
  History: Landmark,
  Geography: Globe,
  'Political Science': Gavel,
  Psychology: Brain,
  Sociology: Users,
};

export function ElectiveSelector({ stream, electives = [], onChange, error }) {
  const config = STREAM_SUBJECTS[stream];
  if (!config) return null;

  const available = config.electives;

  const handleToggle = (subject) => {
    const isSelected = electives.includes(subject);

    if (isSelected) {
      // Deselect
      onChange(electives.filter((e) => e !== subject));
    } else {
      // Select — enforce max
      if (electives.length >= MAX_ELECTIVES) return;
      onChange([...electives, subject]);
    }
  };

  const atMax = electives.length >= MAX_ELECTIVES;

  return (
    <FormSection
      title="Elective Subjects"
      description={`Choose 1 or 2 elective subjects you studied. (Max ${MAX_ELECTIVES})`}
    >
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3" role="group" aria-label="Elective subjects">
        <AnimatePresence>
          {available.map((subject) => {
            const isSelected = electives.includes(subject);
            const isDisabled = !isSelected && atMax;
            const Icon = ELECTIVE_ICONS[subject] || BookOpen;

            return (
              <motion.button
                key={subject}
                type="button"
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.2 }}
                onClick={() => handleToggle(subject)}
                disabled={isDisabled}
                aria-pressed={isSelected}
                className={cn(
                  'flex items-center gap-3 p-4 rounded-xl border-2 text-left transition-all duration-200 cursor-pointer w-full',
                  isSelected
                    ? 'border-stone-900 bg-stone-50 shadow-sm'
                    : 'border-stone-200 bg-white hover:border-stone-300',
                  isDisabled && 'opacity-50 cursor-not-allowed hover:border-stone-200'
                )}
              >
                {/* Icon */}
                <span className={cn(
                  "flex-shrink-0 transition-colors duration-200",
                  isSelected ? "text-stone-900" : "text-stone-500"
                )} aria-hidden="true">
                  <Icon className="w-5 h-5" />
                </span>

                {/* Label */}
                <span className={cn(
                  'text-sm font-medium flex-1',
                  isSelected ? 'text-stone-900' : 'text-stone-700'
                )}>
                  {subject}
                </span>

                {/* Check indicator */}
                <div className={cn(
                  'w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 transition-all duration-200',
                  isSelected
                    ? 'bg-stone-900 text-white border-transparent'
                    : 'border-2 border-stone-300'
                )}>
                  {isSelected && <Check className="w-3 h-3" />}
                </div>
              </motion.button>
            );
          })}
        </AnimatePresence>
      </div>

      {/* Inline validation error */}
      {error && (
        <p role="alert" className="text-sm text-danger mt-2">{error}</p>
      )}
    </FormSection>
  );
}

export default ElectiveSelector;

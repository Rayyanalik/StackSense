import React, { useState, useEffect } from 'react';

interface AnimatedPlaceholderProps {
  texts: string[];
  className?: string;
}

const AnimatedPlaceholder: React.FC<AnimatedPlaceholderProps> = ({ texts, className = '' }) => {
  const [currentText, setCurrentText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isDeleting, setIsDeleting] = useState(false);
  const [typingSpeed, setTypingSpeed] = useState(100);

  useEffect(() => {
    const currentFullText = texts[currentIndex];
    
    if (!isDeleting && currentText === currentFullText) {
      // Pause at the end of typing
      setTimeout(() => setIsDeleting(true), 2000);
      return;
    }

    if (isDeleting && currentText === '') {
      setIsDeleting(false);
      setCurrentIndex((prev) => (prev + 1) % texts.length);
      setTypingSpeed(100);
      return;
    }

    const delta = isDeleting ? -1 : 1;
    const nextText = currentFullText.substring(0, currentText.length + delta);
    
    const timer = setTimeout(() => {
      setCurrentText(nextText);
      setTypingSpeed(isDeleting ? 50 : 100);
    }, typingSpeed);

    return () => clearTimeout(timer);
  }, [currentText, currentIndex, isDeleting, texts, typingSpeed]);

  return (
    <span className={`inline-block ${className}`}>
      {currentText}
      <span className="animate-blink">|</span>
    </span>
  );
};

export default AnimatedPlaceholder; 
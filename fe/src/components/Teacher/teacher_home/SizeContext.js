import { useState, useEffect } from 'react';


export default function useWindowSize() {
  const [windowSize, setWindowSize] = useState({
    width: undefined,
    height: undefined,
  });

  useEffect(() => {
    const handleResize = () => {
      setWindowSize({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };

    window.addEventListener('resize', handleResize);
    handleResize();
    setTimeout(handleResize,100)

    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return windowSize;
}

document.addEventListener('DOMContentLoaded', () => {
    const counters = document.querySelectorAll('.counter');
    const duration = 3000; 
  
    counters.forEach(counter => {
      const target = +counter.dataset.target;
      let start = null;
  
      function step(timestamp) {
        if (!start) start = timestamp;
        const progress = timestamp - start;
        const current = Math.min(
          Math.floor((progress / duration) * target),
          target
        );
        counter.textContent = current.toLocaleString();
        if (progress < duration) {
          window.requestAnimationFrame(step);
        }
      }
  
      window.requestAnimationFrame(step);
    });
  });
/**
 * makes the about section to pop out
 */
document.addEventListener('DOMContentLoaded', () => {
    const about = document.querySelector('.about-section');
  const observer = new IntersectionObserver(([entry], obs) => {
    if (entry.isIntersecting) {
      about.classList.add('visible');
      obs.disconnect();
    }
  }, { threshold: 0.25 });
  observer.observe(about);
});
   
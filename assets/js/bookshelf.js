(() => {
  'use strict';
  const stage = document.querySelector('.bookshelf-stage');
  if (!stage || typeof HTMLDialogElement === 'undefined') return;
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const replay = document.querySelector('.shelf-replay');
  let entranceTimer;
  let active = null;
  let closing = false;
  let previousOverflow = '';

  function enterShelf() {
    clearTimeout(entranceTimer);
    stage.classList.remove('is-ready', 'is-entering');
    if (motion.matches) {
      stage.classList.add('is-ready');
      return;
    }
    // Two frames preserve the spine-first pose before the books turn outward.
    requestAnimationFrame(() => requestAnimationFrame(() => {
      stage.classList.add('is-entering', 'is-ready');
      entranceTimer = setTimeout(() => stage.classList.remove('is-entering'), 1550);
    }));
  }

  function coverFlight(dialog, trigger, reverse = false) {
    const cover = dialog.querySelector('.book-open-cover img');
    const source = trigger.querySelector('img').getBoundingClientRect();
    const target = cover.getBoundingClientRect();
    if (motion.matches || !cover.animate || !source.width || !target.width) return null;
    const shelfPose = `translate(${source.left - target.left}px, ${source.top - target.top}px) scale(${source.width / target.width}, ${source.height / target.height})`;
    const poses = [{ transform: shelfPose, opacity: .7 }, { transform: 'none', opacity: 1 }];
    return cover.animate(reverse ? poses.reverse() : poses, {
      duration: reverse ? 200 : 480,
      easing: 'cubic-bezier(.2,.75,.25,1)',
      fill: 'none'
    });
  }

  function openBook(trigger) {
    if (active) return;
    const dialog = document.getElementById(trigger.getAttribute('aria-controls'));
    if (!dialog) return;
    active = { dialog, trigger };
    previousOverflow = document.documentElement.style.overflow;
    document.documentElement.style.overflow = 'hidden';
    trigger.classList.add('is-selected');
    dialog.showModal();
    dialog.scrollTop = 0;
    coverFlight(dialog, trigger);
    if (!motion.matches && dialog.animate) dialog.animate(
      [{ opacity: 0, transform: 'translateY(12px) scale(.97)' }, { opacity: 1, transform: 'none' }],
      { duration: 240, easing: 'ease-out' }
    );
  }

  async function closeBook() {
    if (!active || closing) return;
    closing = true;
    const { dialog, trigger } = active;
    const flight = coverFlight(dialog, trigger, true);
    if (flight) await flight.finished.catch(() => {});
    dialog.close();
    // The native close event also covers programmatic closure by another script.
  }

  stage.querySelectorAll('.shelf-trigger').forEach(trigger => {
    trigger.addEventListener('click', () => openBook(trigger));
  });
  document.querySelectorAll('.book-dialog').forEach(dialog => {
    dialog.querySelectorAll('[data-close]').forEach(button => button.addEventListener('click', closeBook));
    dialog.addEventListener('cancel', event => { event.preventDefault(); closeBook(); });
    dialog.addEventListener('keydown', event => {
      if (event.key !== 'Tab') return;
      const stops = [...dialog.querySelectorAll('button:not([disabled]), a[href]')];
      const first = stops[0];
      const last = stops[stops.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    });
    dialog.addEventListener('click', event => { if (event.target === dialog) closeBook(); });
    dialog.addEventListener('close', () => {
      if (!active || active.dialog !== dialog) return;
      const trigger = active.trigger;
      trigger.classList.remove('is-selected');
      document.documentElement.style.overflow = previousOverflow;
      active = null;
      closing = false;
      trigger.focus({ preventScroll: true });
    });
  });
  replay.hidden = motion.matches;
  replay.addEventListener('click', enterShelf);
  motion.addEventListener('change', () => {
    replay.hidden = motion.matches;
    if (motion.matches) {
      clearTimeout(entranceTimer);
      stage.classList.remove('is-entering');
      stage.classList.add('is-ready');
      stage.querySelectorAll('.shelf-book').forEach(book => book.getAnimations().forEach(animation => animation.cancel()));
      if (active) active.dialog.getAnimations({ subtree: true }).forEach(animation => animation.cancel());
    }
  });
  stage.dataset.enhanced = 'true';
  enterShelf();
})();

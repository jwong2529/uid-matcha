/* main.js — Matcha Grader jQuery enhancements */

$(function () {

  /* ── Fade-in on load ─────────────────────────────────────────────────── */
  $('body').css('opacity', 0).animate({ opacity: 1 }, 320);

  /* ── Radio option highlight ──────────────────────────────────────────── */
  $(document).on('change', 'input[type="radio"]', function () {
    // Remove active from all siblings
    $(this).closest('.quiz-options').find('.option-label')
      .removeClass('option-selected');
    // Highlight selected
    $(this).closest('.option-label').addClass('option-selected');
  });

  /* ── Option button hover effect (Q1 / Q3 direct submit buttons) ──────── */
  $(document).on('mouseenter', '.option-btn', function () {
    $(this).addClass('option-hover');
  }).on('mouseleave', '.option-btn', function () {
    $(this).removeClass('option-hover');
  });

  /* ── Prevent double-submit on quiz forms ─────────────────────────────── */
  // For direct-submit buttons (Q1, Q3), capture the clicked value into a
  // hidden input BEFORE disabling buttons, so the POST still carries the answer.
  $(document).on('click', '#quiz-form button[type="submit"][name="answer"]', function () {
    var val = $(this).val();
    var $form = $(this).closest('form');
    // Add or update a hidden field that carries the answer value
    var $hidden = $form.find('input[type="hidden"][name="answer"]');
    if ($hidden.length === 0) {
      $hidden = $('<input type="hidden" name="answer">').appendTo($form);
    }
    $hidden.val(val);
  });

  $('#quiz-form').on('submit', function () {
    // Small delay so the hidden input is set before we disable buttons
    var $form = $(this);
    setTimeout(function () {
      $form.find('button[type="submit"]').prop('disabled', true).css('opacity', 0.7);
    }, 50);
  });

  /* ── Animate score ring on results page ─────────────────────────────── */
  const $arc = $('.score-arc');
  if ($arc.length) {
    const target = parseFloat($arc.attr('data-full')) || 0;
    setTimeout(function () {
      $arc.css('transition', 'stroke-dasharray 1.2s cubic-bezier(0.4,0,0.2,1)');
      $arc.attr('stroke-dasharray', target + ' 326.73');
    }, 200);
  }

  /* ── Grade card pop-in ───────────────────────────────────────────────── */
  if ($('.grade-card').length) {
    $('.grade-card').each(function (i) {
      $(this).css({ opacity: 0, transform: 'translateY(18px)' });
      var $card = $(this);
      setTimeout(function () {
        $card.animate({ opacity: 1 }, {
          duration: 350,
          step: function (now) {
            var move = 18 * (1 - now);
            $(this).css('transform', 'translateY(' + move + 'px)');
          }
        });
      }, 80 + i * 100);
    });
  }

});

/* ── Add CSS for radio selected state (can't do :has in older browsers) ── */
$(function () {
  var style = document.createElement('style');
  style.textContent = `
    .option-selected {
      border-color: #6BAF45 !important;
      background: #e8f5df !important;
    }
    .option-selected .option-key {
      color: #2d6a1f;
      font-weight: 700;
    }
  `;
  document.head.appendChild(style);
});

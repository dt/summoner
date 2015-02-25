$().ready(function(){
  function recipients() {
    return jQuery.map($('#recipients').find('li'), function(i) { return $(i).data('email'); });
  }

  function add_remove(email, name) {
    var cur = recipients();
    console.log(email, name, cur);
    if (cur.indexOf(email) == -1) {
      $('#listing').find('.person').each(function(i) {
        if ($(this).data('email') == email) { $(this).parent().addClass('selected');}
      });
      var li = $("<li>").text(name).data('email', email).click(function() {add_remove(email)});
      $('#recipients').append(li);
    } else {
      $('#listing').find('.person').each(function(i) {
        if ($(this).data('email') == email) { $(this).parent().removeClass('selected');}
      });
      $('#recipients').find('li').each(function(i) {
        if ($(this).data('email') == email) { $(this).remove(); }
      });
    }

    if ($('#send').is(':hidden')) {
      $('#send').slideDown();
      $("html, body").animate({ scrollTop: 0 });
    }
  }


  $('.person-box').click(function() {
    var who = $(this).find('.person');
    add_remove(who.data('email'), who.find('.name').text());
  });

  $('#send-submit').click(function() {
    var $btn = $(this).button('loading');
    $alert = $('#alert').removeClass('alert-success alert-danger').hide();

    $.post('/', {
      'recipients': recipients().join(','),
      'msg': $('#msg').val(),
      'sms': $('#send-sms').is(':checked'),
      'email': $('#send-email').is(':checked'),
      'slack': $('#send-slack').is(':checked')
    }, function(whatever) {
      $alert.text("Sent!").addClass('alert-success').slideDown();
       $('#msg').val('');
    }).fail(function(err) {
      $alert.text(err.responseText).addClass('alert-danger').slideDown();
    }).always(function(){
      $btn.button('reset');
    });
  });

  $('#search').fastLiveFilter('#listing', {
    callback: function() {$(window).trigger('scroll');}
  });

  $('.automsg').click(function() { $('#msg').val($(this).data('msg'))});

  $('#search').focus();
})

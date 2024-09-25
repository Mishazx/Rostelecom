$(document).ready(function () {
  $('#requestForm').on('submit', function (e) {
      e.preventDefault();
      let data = {
          lastname: $('#lastname').val(),
          firstname: $('#firstname').val(),
          middlename: $('#middlename').val(),
          phone: $('#phone').val(),
          message: $('#message').val()
      };
      $.ajax({
          url: 'http://backend/api/appeal',
          type: 'POST',
          contentType: 'application/json',
          data: JSON.stringify(data),
          success: function (response) {
              alert('Обращение отправлено!');
          },
          error: function (err) {
              alert('Ошибка при отправке обращения');
          }
      });
  });
});

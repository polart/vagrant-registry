$(function () {
  $(document).ready(function () {
    // ==============================================================
    // Utils
    // ==============================================================

    function getFileHash(file, callback) {
      var blobSlice = File.prototype.slice || File.prototype.mozSlice || File.prototype.webkitSlice,
          chunkSize = 2097152,  // Read in chunks of 2MB
          chunks = Math.ceil(file.size / chunkSize),
          currentChunk = 0,
          spark = new SparkMD5.ArrayBuffer(),
          fileReader = new FileReader();

      fileReader.onload = function (e) {
        spark.append(e.target.result);  // Append array buffer
        currentChunk += 1;

        if (currentChunk < chunks) {
          loadNextChunk();
        } else {
          if (typeof callback === "function") {
            callback(spark.end());
          }
        }
      };

      function loadNextChunk() {
        var start = currentChunk * chunkSize,
            end = ((start + chunkSize) >= file.size) ? file.size : start + chunkSize;

        fileReader.readAsArrayBuffer(blobSlice.call(file, start, end));
      }

      loadNextChunk();
    }

    function showFormErrors(errors) {
      $.each(errors, function (key, value) {
        if (key === 'detail') {
          $form.prepend(
              '<p class="errornote">' + value + '</p>'
          );
          return;
        }

        $('.field-' + key)
            .addClass('errors')
            .prepend(
                '<ul class="errorlist">'
                + '<li>' + value.join(' ') + '</li>'
                + '</ul>'
            );
      });
    }

    function cleanFormErrors(field) {
      if (field) {
        $('.field-' + field)
            .removeClass('errors')
            .find('.errorlist')
            .remove();
      } else {
        $('.errorlist').remove();
        $('.errornote').remove();
        $('.errors').removeClass('errors');
      }
    }

    function enableForm() {
      $('input, select').attr('disabled', false);
    }

    function disableForm() {
      $('input, select').attr('disabled', true);
    }

    function validateFileUpload() {
      cleanFormErrors('file');

      if (!uploadData) {
        showFormErrors({file: ["This field is required."]});
        return false;
      }

      if (!/(\.box)$/i.test(uploadData.files[0].name)) {
        showFormErrors({file: ["Only '*.box' files can be uploaded."]});
        return false;
      }

      return true;
    }

    function updateProgress(text) {
      $progress.text(text);
    }

    function submitForm(formData) {
      var url = $provider.val();
      $.post(url, formData).statusCode({
        201: function (data) {
          uploadUrl = data.url;
          uploadId = data.id;
          uploadData.url = uploadUrl;
          uploadData.submit();
        }
      }).fail(function (jqXHR) {
        enableForm();
        updateProgress('');
        if (jqXHR.responseJSON) {
          showFormErrors(jqXHR.responseJSON);
        } else {
          showFormErrors({
            detail: 'Something went wrong. Please try to submit the form again.'
          });
        }
      });
    }

    function newUploadFormSubmit() {
      var errors = {};
      var provider = $provider.val();

      var isUploadValid = validateFileUpload();
      if (!provider) {
        errors.provider = ['This field is required.'];
      }
      if (!$.isEmptyObject(errors) || !isUploadValid) {
        showFormErrors(errors);
        return;
      }

      var formData = {
        file_size: uploadData.files[0].size,
        checksum_type: 'md5'
      };

      disableForm();

      if (uploadUrl) {
        uploadData.url = uploadUrl;
        uploadData.submit();
        return;
      }

      if (fileHash) {
        formData.checksum = fileHash;
        submitForm(formData);
      } else {
        updateProgress('Computing checksum...');
        getFileHash(uploadData.files[0], function (hash) {
          formData.checksum = hash;
          fileHash = hash;
          submitForm(formData);
        });
      }
    }

    function editUploadFormSubmit() {
      if (!validateFileUpload()) {
        return;
      }

      disableForm();

      uploadData.url = uploadUrl;
      if (fileHash) {
        uploadData.submit();
      } else {
        updateProgress('Computing checksum...');
        getFileHash(uploadData.files[0], function (hash) {
          if (originalHash !== hash) {
            showFormErrors({
              file: ["Checksum of selected file doesn't match the original one. " +
                "Please select original file."]
            });
            enableForm();
            return;
          }
          fileHash = hash;
          uploadData.submit();
        });
      }
    }

    // ==============================================================
    // Event handlers
    // ==============================================================

    function onFormSubmit(e) {
      e.preventDefault();
      cleanFormErrors();

      if (isNewUpload) {
        newUploadFormSubmit();
      } else {
        editUploadFormSubmit();
      }
    }

    function onFileUploadAdd(e, data) {
      uploadData = data;
      fileHash = null;
      $('#id_file').next().text(data.files[0].name);
    }

    function onFileUploadProgress(e, data) {
      var progress = parseInt(data.loaded / data.total * 100, 10);
      updateProgress('Uploading progress: ' + progress + '%');
    }

    function onFileUploadDone() {
      updateProgress('Box uploaded!');
      if (isNewUpload) {
        if (saveType === '_save') {
          window.location.href = baseUrl;
        } else if (saveType === '_continue') {
          window.location.href = baseUrl + uploadId + '/change/';
        } else if (saveType === '_addanother') {
          window.location.reload();
        }
      } else {
        if (saveType === '_save') {
          window.location.href = baseUrl;
        } else if (saveType === '_continue') {
          window.location.reload();
        } else if (saveType === '_addanother') {
          window.location.href = baseUrl + 'add/';
        }
      }
    }

    function onFileUploadFail(e, data) {
      enableForm();
      cleanFormErrors();

      var jqXHR = data.jqXHR;

      if (jqXHR && jqXHR.status === 416) {  // Requested Range Not Satisfiable
        data.uploadedBytes = data.jqXHR.responseJSON.offset;
        data.submit();
        return;
      }
      if (jqXHR && jqXHR.responseJSON) {
        showFormErrors(jqXHR.responseJSON);
      } else {
        showFormErrors({
          detail: 'Something went wrong. Please try to submit the form again.'
        });
      }
    }

    // ==============================================================
    // Initialisation
    // ==============================================================

    var $form = $('#boxupload_form');
    var $provider = $('#id_provider');
    var $file = $('#id_file');

    var csrftoken = $('input[name="csrfmiddlewaretoken"]').val();
    var saveType = '_save';
    var baseUrl = '/admin/boxes/boxupload/';
    var originalHash = $('.field-checksum').find('div.readonly').text();
    var fileHash = null;
    var uploadData = null;
    var uploadId = null;
    var uploadUrl = $('#id_api_upload_url').val();
    var isNewUpload = !uploadUrl;

    // CSRF header needed for API session authentication
    $.ajaxSetup({
      beforeSend: function(xhr) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    });

    // Custom upload button
    $file.after(
        '<label for="id_file">Choose box file</label>' +
        '<span id="upload_progress"></span>'
    );
    var $progress = $('#upload_progress');

    // Init file upload
    $file.fileupload({
      dataType: "json",
      type: 'PUT',
      sequentialUploads: true,
      maxChunkSize: 10000000,
      autoUpload: false,
      multipart: false
    });

    // ==============================================================
    // Bind event handlers
    // ==============================================================
    $('input[type="submit"]').on('click', function () { saveType = this.name; });
    $form.on('submit', onFormSubmit);
    $file.on('fileuploadadd', onFileUploadAdd);
    $file.on('fileuploadprogress', onFileUploadProgress);
    $file.on('fileuploaddone', onFileUploadDone);
    $file.on('fileuploadfail', onFileUploadFail);
  });
});

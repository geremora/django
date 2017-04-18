View      = require 'lib/view'

module.exports = class AppView extends View
    el: 'body.application'

    initialize: ->
        # Case detail tabs
        $('#case-detail-tab a:first').tab('show')

        # Disabled transition button popovers
        $('.case-transition-button-disabled').popover
            html: yes
            content: ->
                ($ @).next().html()

        # Observed notes popovers
        $('.case-event-observed-notes').popover
            html: yes
            content: ->
                ($ @).next().html()

        # DateTime Picker Init
        $('.datetimepicker').datetimepicker
            format: 'YYYY-MM-DD HH:mm:ss'
            icons:
                up: 'fa fa-chevron-up'
                down: 'fa fa-chevron-down'
                next: 'fa fa-chevron-right'
                previous: 'fa fa-chevron-left'
                time: 'fa fa-clock-o'
                date: 'fa fa-calendar'
                clear: 'fa fa-trash-o'
                close: 'fa fa-times'
            sideBySide: yes
            allowInputToggle: yes

        # Select 2 Init
        $('select').not('#id_basic_info_step-contacts')
        .not('.select-with-ajax').select2
            width: '100%'

        # Contacts search and select with ajax
        $('.select-with-ajax').select2
            width: '100%'
            minimumInputLength: 2
            placeholder: 'Busqueda de contactos'
            initSelection: (element, callback) ->
                ids = ($ element).val()

                if ids
                    $.getJSON "/contacts/ajax/?ids=#{ids}", (data) ->
                        if data.length > 0
                           return callback data[0]
                        return callback data

            formatNoMatches: (term) ->
                if term
                    return "No se encontró \"#{term}\""
                else
                    return 'Entre un nombre'
            ajax:
                url: '/contacts/ajax/'
                dataType: 'json'
                data: (term, page) ->
                    q: term
                    page_limit: 20
                    type: ($ @).data('contact-type')

                results: (data, page) ->
                    { results: data }


        $('.contact-type-list-ajax').select2
            width: '100%'
            multiple: false
            minimumInputLength: 2
            placeholder: 'Busqueda de Contactos'
            initSelection: (element, callback) ->
                ids = ($ element).val()

                if ids
                    $.getJSON "/contacts/ajax/?ids=#{ids}", (data) ->
                        if data.length > 0
                           return callback data[0]
                        return callback data

            formatNoMatches: (term) ->
                if term
                    return "No se encontró \"#{term}\""
                else
                    return 'Entre un nombre'
            formatSelection: (data) ->
                return data.text
            ajax:
                url: '/contacts/ajax/'
                dataType: 'json'
                data: (term, page) ->
                    q: term
                    page_limit: 20,
                    case_type: $('#id_basic_info_step-case_type').val()

                results: (data, page) ->
                    { results: data }

        # Contacts search and select multiple with ajax
        $('.contact-list-ajax').select2
            width: '100%'
            multiple: yes
            minimumInputLength: 2
            placeholder: 'Busqueda de contactos'
            initSelection: (element, callback) ->
                ids = ($ element).val()

                if ids.indexOf('[') > -1 || ids.indexOf(']') > -1
                    ids = ids.replace('[', '')
                    ids = ids.replace(']', '')
                    ($ element).val(ids)

                if ids
                    $.getJSON "/contacts/ajax/?ids=#{ids}", (data) ->
                        callback data

            formatNoMatches: (term) ->
                if term
                    return "No se encontró \"#{term}\""
                else
                    return 'Entre un nombre'
            ajax:
                url: '/contacts/ajax/'
                dataType: 'json'
                data: (term, page) ->
                    q: term
                    page_limit: 20

                results: (data, page) ->
                    { results: data }

        # Request permision listener
        $('.request-button').click () ->
            codename = $(this).attr('data-codename');

            $('#perm-codename').val(codename);
            $('#request-modal').modal('show');

        # Load merged cases
        $loadMergedButton = $(document)
        $mergeCaseContainer = $('.merged-case-container')

        $loadMergedButton.on 'click', '.load-merged-cases-button', (event) ->
            $button = $(event.currentTarget)

            oldText = $button.text()
            $button.text 'Cargando...'
            $button.attr 'disabled', 'diabled'

            console.log 'hit!'

            id = $button.data 'case-id'
            nextPage = $button.data('case-next-page') or 1

            console.log id, nextPage

            $.get("/cases/#{id}/merged/?page=#{nextPage}", (data) ->
                if nextPage == 1
                    $mergeCaseContainer.html data
                else
                    $mergeCaseContainer.append data

                $selectAllMergedCases = $('.select-all-merged-cases')

                $selectAllMergedCases.each ->
                  $(this).click ->
                    el = $(this);
                    el.parents('table').find('tbody tr td input:checkbox').each ->
                      $(this).prop 'checked', el.prop('checked')

                $button.remove()
            ).fail (err) ->
                msg = '<div class="alert alert-error">Error, trate de nuevo.<div>'
                $mergeCaseContainer.prepend msg

                $button.text oldText
                $button.removeAttr 'disabled'


        # Initialize s3direct uploader
        # This will find all fields with .s3direct-upload class
        $inputText = $('.s3direct-upload')
        $form = $inputText.parents('form')

        # Make the text input into a file picker
        inputName = $inputText.attr('name')
        className = $inputText.attr('class')

        if $inputText.val() == ''
            $inputText.after("<input type='file' name='#{inputName}' class='#{className}'>")
            $inputText.remove()
            $inputFilePicker = $('.s3direct-upload')
        else
            theValue = $inputText.val()
            $inputText.after("<input type='hidden' name='#{inputName}' class='#{className}' value='#{theValue}'>")
            $inputText.after("<span class='s3direct-upload-progress'>#{theValue}</span>")
            $inputText.remove()
            $inputFilePicker = $('.s3direct-upload')

        $inputFilePicker.on 'change', (event) ->
            $('.btn.btn-grey').addClass('disabled')

            s3upload = new S3Upload
                file_dom_selector: '.s3direct-upload'
                s3_sign_put_url: '/cases/ajax/s3signature/'

                onProgress: (percent, status, public_url, file) ->
                    $form.on 'submit', (event) ->
                        event.preventDefault()

                    $progressLabel = $('.s3direct-upload-progress')
                    $inputFilePicker.hide()

                    if $progressLabel.length > 0
                        $progressLabel.replaceWith("<span class='s3direct-upload-progress'>#{percent}% Subiendo archivo...</span>")
                    else
                        $inputFilePicker.after("<span class='s3direct-upload-progress'>#{percent}% Subiendo archivo...</span>")

                onFinishS3Put: (public_url, file, objectName) ->
                    $form.off('submit')

                    $('.s3direct-upload-progress').text("Completedo: #{file.name}")

                    name = $inputFilePicker.attr('name')
                    $inputFilePicker.after("<input type='hidden' name='#{name}' value='#{objectName}'>")

                    $inputFilePicker.remove()
                    $('.btn.btn-grey').removeClass('disabled')

                onError: (status, file) ->
                    $('.s3direct-upload-progress').text("Error, trate de nuevo: #{status}")
                    $inputFilePicker.show().val('')

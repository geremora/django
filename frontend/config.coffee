exports.config =
    # See docs at http://brunch.readthedocs.org/en/latest/config.html.
    paths:
        public: '../static/'

    coffeelint:
        pattern: /^app\/.*\.coffee$/
        options:
            indentation:
                value: 4
                level: "error"

            max_line_length:
                value: 100
                level: "error"


    files:
        javascripts:
            joinTo:
                'javascripts/app.js': /^app/
                'javascripts/vendor.js': /^vendor/
                'test/javascripts/test.js': /^test(\/|\\)(?!vendor)/
                'test/javascripts/test-vendor.js': /^test(\/|\\)(?=vendor)/
            order:
                # Files in `vendor` directories are compiled before other files
                # even if they aren't specified in order.
                before: [
                    'vendor/scripts/jquery.js'
                    'vendor/scripts/lodash.js'
                    'vendor/scripts/backbone.js'
                    'vendor/scripts/bootstrap.js'
                    'vendor/scripts/bootstrap-datetimepicker.min.js'
                    'vendor/scripts/RelatedObjectLookups.js'
                    'vendor/scripts/select2.js'
                    'vendor/scripts/s3upload.js'
                    'vendor/scripts/underscore.js'
                ]

        stylesheets:
            joinTo: 'stylesheets/app.css'
            order:
                before: [
                    'vendor/styles/bootstrap.css'
                    'vendor/styles/bootstrap-wysihtml5.css'
                    'vendor/styles/select2.css'
                ]
                after: ['vendor/styles/helpers.css']

        templates:
            joinTo: 'javascripts/app.js'

# App Namespace
# Change `Casp` to your app's name
@Casp ?= {}
Casp.Routers ?= {}
Casp.Views ?= {}
Casp.Models ?= {}
Casp.Collections ?= {}

$ ->
    # Load App Helpers
    require 'lib/app_helpers'

    # Initialize App
    Casp.Views.AppView = new AppView = require 'views/app_view'

    # Initialize Backbone History
    Backbone.history.start pushState: yes

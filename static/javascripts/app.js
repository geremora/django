(function() {
  'use strict';

  var globals = typeof window === 'undefined' ? global : window;
  if (typeof globals.require === 'function') return;

  var modules = {};
  var cache = {};
  var aliases = {};
  var has = ({}).hasOwnProperty;

  var expRe = /^\.\.?(\/|$)/;
  var expand = function(root, name) {
    var results = [], part;
    var parts = (expRe.test(name) ? root + '/' + name : name).split('/');
    for (var i = 0, length = parts.length; i < length; i++) {
      part = parts[i];
      if (part === '..') {
        results.pop();
      } else if (part !== '.' && part !== '') {
        results.push(part);
      }
    }
    return results.join('/');
  };

  var dirname = function(path) {
    return path.split('/').slice(0, -1).join('/');
  };

  var localRequire = function(path) {
    return function expanded(name) {
      var absolute = expand(dirname(path), name);
      return globals.require(absolute, path);
    };
  };

  var initModule = function(name, definition) {
    var hot = null;
    hot = hmr && hmr.createHot(name);
    var module = {id: name, exports: {}, hot: hot};
    cache[name] = module;
    definition(module.exports, localRequire(name), module);
    return module.exports;
  };

  var expandAlias = function(name) {
    return aliases[name] ? expandAlias(aliases[name]) : name;
  };

  var _resolve = function(name, dep) {
    return expandAlias(expand(dirname(name), dep));
  };

  var require = function(name, loaderPath) {
    if (loaderPath == null) loaderPath = '/';
    var path = expandAlias(name);

    if (has.call(cache, path)) return cache[path].exports;
    if (has.call(modules, path)) return initModule(path, modules[path]);

    throw new Error("Cannot find module '" + name + "' from '" + loaderPath + "'");
  };

  require.alias = function(from, to) {
    aliases[to] = from;
  };

  var extRe = /\.[^.\/]+$/;
  var indexRe = /\/index(\.[^\/]+)?$/;
  var addExtensions = function(bundle) {
    if (extRe.test(bundle)) {
      var alias = bundle.replace(extRe, '');
      if (!has.call(aliases, alias) || aliases[alias].replace(extRe, '') === alias + '/index') {
        aliases[alias] = bundle;
      }
    }

    if (indexRe.test(bundle)) {
      var iAlias = bundle.replace(indexRe, '');
      if (!has.call(aliases, iAlias)) {
        aliases[iAlias] = bundle;
      }
    }
  };

  require.register = require.define = function(bundle, fn) {
    if (typeof bundle === 'object') {
      for (var key in bundle) {
        if (has.call(bundle, key)) {
          require.register(key, bundle[key]);
        }
      }
    } else {
      modules[bundle] = fn;
      delete cache[bundle];
      addExtensions(bundle);
    }
  };

  require.list = function() {
    var list = [];
    for (var item in modules) {
      if (has.call(modules, item)) {
        list.push(item);
      }
    }
    return list;
  };

  var hmr = globals._hmr && new globals._hmr(_resolve, require, modules, cache);
  require._cache = cache;
  require.hmr = hmr && hmr.wrap;
  require.brunch = true;
  globals.require = require;
})();

(function() {
var global = window;
var __makeRelativeRequire = function(require, mappings, pref) {
  var none = {};
  var tryReq = function(name, pref) {
    var val;
    try {
      val = require(pref + '/node_modules/' + name);
      return val;
    } catch (e) {
      if (e.toString().indexOf('Cannot find module') === -1) {
        throw e;
      }

      if (pref.indexOf('node_modules') !== -1) {
        var s = pref.split('/');
        var i = s.lastIndexOf('node_modules');
        var newPref = s.slice(0, i).join('/');
        return tryReq(name, newPref);
      }
    }
    return none;
  };
  return function(name) {
    if (name in mappings) name = mappings[name];
    if (!name) return;
    if (name[0] !== '.' && pref) {
      var val = tryReq(name, pref);
      if (val !== none) return val;
    }
    return require(name);
  }
};
require.register("initialize.coffee", function(exports, require, module) {
if (this.Casp == null) {
  this.Casp = {};
}

if (Casp.Routers == null) {
  Casp.Routers = {};
}

if (Casp.Views == null) {
  Casp.Views = {};
}

if (Casp.Models == null) {
  Casp.Models = {};
}

if (Casp.Collections == null) {
  Casp.Collections = {};
}

$(function() {
  var AppView;
  require('lib/app_helpers');
  Casp.Views.AppView = new (AppView = require('views/app_view'));
  return Backbone.history.start({
    pushState: true
  });
});

});

require.register("lib/app_helpers.coffee", function(exports, require, module) {
(function() {
  Swag.Config.partialsPath = '../views/templates/';
  return (function() {
    var console, dummy, method, methods, results;
    console = window.console = window.console || {};
    method = void 0;
    dummy = function() {};
    methods = 'assert,count,debug,dir,dirxml,error,exception, group,groupCollapsed,groupEnd,info,log,markTimeline, profile,profileEnd,time,timeEnd,trace,warn'.split(',');
    results = [];
    while (method = methods.pop()) {
      results.push(console[method] = console[method] || dummy);
    }
    return results;
  })();
})();

});

require.register("lib/collection.coffee", function(exports, require, module) {
var Collection,
  extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

module.exports = Collection = (function(superClass) {
  extend(Collection, superClass);

  function Collection() {
    return Collection.__super__.constructor.apply(this, arguments);
  }

  Collection.prototype.resetSilent = function(models) {
    return this.reset(models, {
      silent: true
    });
  };

  return Collection;

})(Backbone.Collection);

});

require.register("lib/model.coffee", function(exports, require, module) {
var Model,
  extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty,
  slice = [].slice;

module.exports = Model = (function(superClass) {
  extend(Model, superClass);

  function Model() {
    return Model.__super__.constructor.apply(this, arguments);
  }

  Model.prototype.setSilent = function(attributes) {
    return this.set(attributes, {
      silent: true
    });
  };

  Model.prototype.push = function() {
    var attr, attribute, obj, values;
    attribute = arguments[0], values = 2 <= arguments.length ? slice.call(arguments, 1) : [];
    obj = {};
    attr = this.get(attribute);
    attr.push.apply(attr, values);
    obj[attribute] = attr;
    return this.set(obj);
  };

  Model.prototype.pop = function(attribute) {
    var attr, obj;
    obj = {};
    attr = this.get(attribute);
    attr.pop();
    obj[attribute] = attr;
    return this.set(obj);
  };

  Model.prototype.reverse = function(attribute) {
    var attr, obj;
    obj = {};
    attr = this.get(attribute);
    attr.reverse();
    obj[attribute] = attr;
    return this.set(obj);
  };

  Model.prototype.shift = function(attribute) {
    var attr, obj;
    obj = {};
    attr = this.get(attribute);
    attr.shift();
    obj[attribute] = attr;
    return this.set(obj);
  };

  Model.prototype.unshift = function() {
    var attr, attribute, obj, values;
    attribute = arguments[0], values = 2 <= arguments.length ? slice.call(arguments, 1) : [];
    obj = {};
    attr = this.get(attribute);
    attr.unshift.apply(attr, values);
    obj[attribute] = attr;
    return this.set(obj);
  };

  Model.prototype.splice = function() {
    var attr, attribute, obj, values;
    attribute = arguments[0], values = 2 <= arguments.length ? slice.call(arguments, 1) : [];
    obj = {};
    attr = this.get(attribute);
    attr.splice.apply(attr, values);
    obj[attribute] = attr;
    return this.set(obj);
  };

  Model.prototype.add = function() {
    var attr, attribute, i, len, obj, value, values;
    attribute = arguments[0], values = 2 <= arguments.length ? slice.call(arguments, 1) : [];
    obj = {};
    attr = this.get(attribute);
    for (i = 0, len = values.length; i < len; i++) {
      value = values[i];
      attr += value;
    }
    obj[attribute] = attr;
    return this.set(obj);
  };

  Model.prototype.subtract = function() {
    var attr, attribute, i, len, obj, value, values;
    attribute = arguments[0], values = 2 <= arguments.length ? slice.call(arguments, 1) : [];
    obj = {};
    attr = this.get(attribute);
    for (i = 0, len = values.length; i < len; i++) {
      value = values[i];
      attr -= value;
    }
    obj[attribute] = attr;
    return this.set(obj);
  };

  Model.prototype.divide = function() {
    var attr, attribute, i, len, obj, value, values;
    attribute = arguments[0], values = 2 <= arguments.length ? slice.call(arguments, 1) : [];
    obj = {};
    attr = this.get(attribute);
    for (i = 0, len = values.length; i < len; i++) {
      value = values[i];
      attr /= value;
    }
    obj[attribute] = attr;
    return this.set(obj);
  };

  Model.prototype.multiply = function() {
    var attr, attribute, i, len, obj, value, values;
    attribute = arguments[0], values = 2 <= arguments.length ? slice.call(arguments, 1) : [];
    obj = {};
    attr = this.get(attribute);
    for (i = 0, len = values.length; i < len; i++) {
      value = values[i];
      attr *= value;
    }
    obj[attribute] = attr;
    return this.set(obj);
  };

  return Model;

})(Backbone.Model);

});

require.register("lib/view.coffee", function(exports, require, module) {
var Model, View,
  extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

Model = require('lib/model');

module.exports = View = (function(superClass) {
  extend(View, superClass);

  function View() {
    return View.__super__.constructor.apply(this, arguments);
  }

  View.prototype.debug = false;

  View.prototype.startDebugging = function() {
    this.on(this.cid + ":initialize", function() {
      return console.debug("Initialized " + this.name, this);
    });
    this.on(this.cid + ":render", function() {
      return console.debug("Rendered " + this.name, this);
    });
    this.on(this.cid + ":update", function() {
      return console.debug("Updated " + this.name, this);
    });
    return this.on(this.cid + ":destroy", function() {
      return console.debug("Destroyed " + this.name, this);
    });
  };

  View.prototype.type = 'view';

  View.prototype.name = null;

  View.prototype.autoRender = false;

  View.prototype.rendered = false;

  View.prototype.model = new Model();

  View.prototype.template = function() {
    return '';
  };

  View.prototype.html = function(dom) {
    this.$el.html(dom);
    this.trigger(this.cid + ":" + (this.rendered ? 'update' : 'render'), this);
    return this.$el;
  };

  View.prototype.append = function(dom) {
    this.$el.append(dom);
    this.trigger(this.cid + ":" + (this.rendered ? 'update' : 'render'), this);
    return this.$el;
  };

  View.prototype.prepend = function(dom) {
    this.$el.prepend(dom);
    this.trigger(this.cid + ":" + (this.rendered ? 'update' : 'render'), this);
    return this.$el;
  };

  View.prototype.after = function(dom) {
    this.$el.after(dom);
    this.trigger(this.cid + ":update", this);
    return this.$el;
  };

  View.prototype.before = function(dom) {
    this.$el.after(dom);
    this.trigger(this.cid + ":update", this);
    return this.$el;
  };

  View.prototype.css = function(css) {
    this.$el.css(css);
    this.trigger(this.cid + ":update", this);
    return this.$el;
  };

  View.prototype.find = function(selector) {
    return this.$el.find(selector);
  };

  View.prototype.delegate = function(event, selector, handler) {
    if (arguments.length === 2) {
      handler = selector;
    }
    handler = handler.bind(this);
    if (arguments.length === 2) {
      return this.$el.on(event, handler);
    } else {
      return this.$el.on(event, selector, handler);
    }
  };

  View.prototype.bootstrap = function() {};

  View.prototype.initialize = function() {
    this.bootstrap();
    this.name = this.name || this.constructor.name;
    if (this.debug === true) {
      this.startDebugging();
    }
    if (this.autoRender === true) {
      this.render();
    }
    return this.trigger(this.cid + ":initialize", this);
  };

  View.prototype.getRenderData = function() {
    var ref;
    return (ref = this.model) != null ? ref.toJSON() : void 0;
  };

  View.prototype.render = function() {
    this.trigger(this.cid + ":render:before", this);
    this.$el.attr('data-cid', this.cid);
    this.html(this.template(this.getRenderData()));
    this.rendered = true;
    this.trigger(this.cid + ":render:after", this);
    return this;
  };

  View.prototype.destroy = function(keepDOM) {
    var ref;
    if (keepDOM == null) {
      keepDOM = false;
    }
    this.trigger(this.cid + ":destroy:before", this);
    if (keepDOM) {
      this.dispose();
    } else {
      this.remove();
    }
    if ((ref = this.model) != null) {
      ref.destroy();
    }
    return this.trigger(this.cid + ":destroy:after", this);
  };

  return View;

})(Backbone.View);

});

require.register("routers/app_router.coffee", function(exports, require, module) {
var AppRouter,
  extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

module.exports = AppRouter = (function(superClass) {
  extend(AppRouter, superClass);

  function AppRouter() {
    return AppRouter.__super__.constructor.apply(this, arguments);
  }

  AppRouter.prototype.routes = {
    '': function() {}
  };

  return AppRouter;

})(Backbone.Router);

});

require.register("views/app_view.coffee", function(exports, require, module) {
var AppView, View,
  extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

View = require('lib/view');

module.exports = AppView = (function(superClass) {
  extend(AppView, superClass);

  function AppView() {
    return AppView.__super__.constructor.apply(this, arguments);
  }

  AppView.prototype.el = 'body.application';

  AppView.prototype.initialize = function() {
    var $form, $inputFilePicker, $inputText, $loadMergedButton, $mergeCaseContainer, className, inputName, theValue;
    $('#case-detail-tab a:first').tab('show');
    $('.case-transition-button-disabled').popover({
      html: true,
      content: function() {
        return ($(this)).next().html();
      }
    });
    $('.case-event-observed-notes').popover({
      html: true,
      content: function() {
        return ($(this)).next().html();
      }
    });
    $('.datetimepicker').datetimepicker({
      format: 'YYYY-MM-DD HH:mm',
      icons: {
        up: 'fa fa-chevron-up',
        down: 'fa fa-chevron-down',
        next: 'fa fa-chevron-right',
        previous: 'fa fa-chevron-left',
        time: 'fa fa-clock-o',
        date: 'fa fa-calendar',
        clear: 'fa fa-trash-o',
        close: 'fa fa-times'
      },
      sideBySide: true,
      allowInputToggle: true,
      showTodayButton: true
    });
    $('select').not('#id_basic_info_step-contacts').not('.select-with-ajax').select2({
      width: '100%'
    });

    function hideHeadAgency() {
      dropdown = document.getElementById('id_contact_type').options[document.getElementById('id_contact_type').selectedIndex];
        $('#id_head_agency').hide();
        $('#id_head_agency').parent().hide();
        $('#id_head_agency').parent().parent().hide();

        //Hides institutional_name field
        $('#id_institutional_name').hide();
        $('#id_institutional_name').parent().hide();
        $('#id_institutional_name').parent().parent().hide();

        $('#id_first_name').hide();
        $('#id_first_name').parent().hide();
        $('#id_first_name').parent().parent().hide();

        //Hides last_name field
        $('#id_last_name').hide();
        $('#id_last_name').parent().hide();
        $('#id_last_name').parent().parent().hide();
      
      if(dropdown.value == "1") {

        $('#id_head_agency').show();
        $('#id_head_agency').parent().show();
        $('#id_head_agency').parent().parent().show();

        //Shows institutional_name field
        $('#id_institutional_name').show();
        $('#id_institutional_name').parent().show();
        $('#id_institutional_name').parent().parent().show();

      } else if(dropdown.value == "2" || dropdown.value == "3" || dropdown.value == "6") {

        $('#id_first_name').show();
        $('#id_first_name').parent().show();
        $('#id_first_name').parent().parent().show();

        //Shows last_name field
        $('#id_last_name').show();
        $('#id_last_name').parent().show();
        $('#id_last_name').parent().parent().show();

      } else if (dropdown.value == "4" || dropdown.value == "5"){
        //Shows institutional_name field
        $('#id_institutional_name').show();
        $('#id_institutional_name').parent().show();
        $('#id_institutional_name').parent().parent().show();
      }
    }

    function hideElementAndParents(element){
      element.hide();
      element.parent().hide();
      element.parent().parent().hide();

    }

    function showElementAndParents(element){
      element.show();
      element.parent().show();
      element.parent().parent().show();

    }

    function hideEventsFieldHandler() {
      dropdown = document.getElementById('id_event_type').options[document.getElementById('id_event_type').selectedIndex];
  
      event_type_id = dropdown.value;


      $.getJSON("/events/ajax/?event_type_id=" + event_type_id, function(data) {
            event_type = data;
            $("#id_requires_terms").prop("checked", event_type.requires_terms);
            $("#id_requires_acceptance").prop("checked", event_type.requires_acceptance);
            $("#id_requires_notification").prop("checked", event_type.requires_notification);
            
            if (event_type.requires_acceptance){
             
              showElementAndParents($('#id_requires_acceptance'));
              showElementAndParents($('#id_accepted'));
            }else{
              hideElementAndParents($('#id_requires_acceptance'));
              hideElementAndParents($('#id_accepted'));
            }

            if (event_type.requires_terms){
             
              showElementAndParents($('#id_requires_terms'));
              showElementAndParents($('#id_date_terms_expiration'));
              $('#id_date_terms_expiration').parent().parent().parent().show();
      
            }else{
              hideElementAndParents($('#id_requires_terms'));
              hideElementAndParents($('#id_date_terms_expiration'));
              $('#id_date_terms_expiration').parent().parent().parent().hide();
            }

            if (event_type.requires_notification){
             
              showElementAndParents($('#id_requires_notification'));
              showElementAndParents($('#id_date_notification'));
              $('#id_date_notification').parent().parent().parent().show();

            }else{
              hideElementAndParents($('#id_requires_notification'));
              hideElementAndParents($('#id_date_notification'));

              $('#id_date_notification').parent().parent().parent().hide();
            }

            if (event_type.requires_parties){
              showElementAndParents($('#id_party'));

            }else{
              hideElementAndParents($('#id_party'));
            }

             if (event_type.requires_generate_by){
              showElementAndParents($('#id_generate_by'));

            }else{
              hideElementAndParents($('#id_generate_by'));
            }


            
      });

    }

    
    function changeDateEmittedEvent(date_emitted) {
      dropdown = document.getElementById('id_event_type').options[document.getElementById('id_event_type').selectedIndex];

      event_type_id = dropdown.value;

      $.getJSON("/events/ajax/?event_type_id=" + event_type_id, function(data) {
        event_type = data;

        if (event_type.requires_terms && event_type.amount_days_terms > 0){

          var date_terms_expiration = new Date();
          date_terms_expiration.setDate(date_emitted.getDate() + event_type.amount_days_terms);
      
          $('#id_date_terms_expiration').datetimepicker( {format: 'YYYY-MM-DD HH:mm'}).data("DateTimePicker").date(date_terms_expiration);
          
        }

      });



    }

    $('.datetimepicker').datetimepicker().on('dp.change', function(e){
      datepicker = $(e.target).children()[0];
      if (datepicker && datepicker.name == 'date_emitted'){

        changeDateEmittedEvent(new Date(datepicker.value));
      
      }
    })

    function changeCaseType() {

      dropdown = document.getElementById('id_basic_info_step-case_type').options[document.getElementById('id_basic_info_step-case_type').selectedIndex];

      case_type_id = dropdown.value;

        $.getJSON("/cases/ajax/case_category/?case_type_id=" + case_type_id, function(data) {
          case_categories = data;

          
          ('#id_basic_info_step-case_category').selectedIndex = -1
          $('#id_basic_info_step-case_category').empty();
          $.each(case_categories, function(i, obj){
              $('#id_basic_info_step-case_category').append($('<option>').text(obj.name).attr('value', obj.id));
          });

      });
    }
    


    window.onload = function() {

      if (document.getElementById('id_contact_type')){
        hideHeadAgency(); // Hides head agency if nothing is selected
        document.getElementById('id_contact_type').onchange = hideHeadAgency;
      }
      if (document.getElementById('id_event_type')){
      
        document.getElementById('id_event_type').onchange = hideEventsFieldHandler;
        

      }

      if (document.getElementById('id_basic_info_step-case_type')){
      
        document.getElementById('id_basic_info_step-case_type').onchange = changeCaseType;
        
      }


     


    };


    $('.select-with-ajax').select2({
      width: '100%',
      minimumInputLength: 2,
      placeholder: 'Busqueda de contactos',
      initSelection: function(element, callback) {
        var ids;
        ids = ($(element)).val();
        if (ids) {
          return $.getJSON("/contacts/ajax/?ids=" + ids, function(data) {
            if (data.length > 0) {
              return callback(data[0]);
            }
            return callback(data);
          });
        }
      },
      formatNoMatches: function(term) {
        if (term) {
          return "No se encontró \"" + term + "\" " + "<a href='/cases/add/contact' onclick='return showAddAnotherPopup(this);' class='add-another'>Agregar</a>";
        } else {
          return 'Entre un nombre';
        }
      },
      ajax: {
        url: '/contacts/ajax/',
        dataType: 'json',
        data: function(term, page) {
          return {
            q: term,
            page_limit: 20,
            type: ($(this)).data('contact-type')
          };
        },
        results: function(data, page) {
          return {
            results: data
          };
        }
      }
    });

    $('.case-list-ajax').select2({
      width: '100%',
      multiple: true,
      minimumInputLength: 2,
      placeholder: 'Búsqueda de Casos',
      initSelection: function(element, callback) {
    
        return $.getJSON("/cases/ajax/", function(data) {
            if (data.length > 0) {
              return callback(data[0]);
            }
            return callback(data);
        });
        
      },
      formatNoMatches: function(term) {
        if (term) {
          return "Este caso no esta disponible para está opción \"" + term + "\"";
        } else {
          return 'Ingrese un número de caso';
        }
      },
      formatSelection: function(data) {
        return data.text;
      },
      ajax: {
        url: '/cases/ajax/',
        dataType: 'json',
        data: function(term, page) {
          console.log(this)
          return {
            q: term,
            page_limit: 20,
            case_type: ($(this)).data('case-type'),
            only_no_merged: ($(this)).data('only-no-merged-case'),
            case_id: ($(this)).data('case-id')
          };
        },
        results: function(data, page) {
          return {
            results: data
          };
        }
      }
    });

    $('.contact-type-list-ajax').select2({
      width: '100%',
      multiple: false,
      minimumInputLength: 2,
      placeholder: 'Busqueda de Contactos',
      initSelection: function(element, callback) {
        var ids;
        ids = ($(element)).val();
        if (ids) {
          return $.getJSON("/contacts/ajax/?ids=" + ids, function(data) {
            if (data.length > 0) {
              return callback(data[0]);
            }
            return callback(data);
          });
        }
      },
      formatNoMatches: function(term) {
        if (term) {
          return "No se encontró \"" + term + "\" " + "<a href='/cases/add/contact' onclick='return showAddAnotherPopup(this);' class='add-another'>Agregar</a>";
        } else {
          return 'Entre un nombre';
        }
      },
      formatSelection: function(data) {
        return data.text;
      },
      ajax: {
        url: '/contacts/ajax/',
        dataType: 'json',
        data: function(term, page) {
          return {
            q: term,
            page_limit: 20,
            case_type: $('#id_basic_info_step-case_type').val()
          };
        },
        results: function(data, page) {
          return {
            results: data
          };
        }
      }
    });
    $('.contact-list-ajax').select2({
      width: '100%',
      multiple: true,
      minimumInputLength: 2,
      placeholder: 'Busqueda de contactos',
      initSelection: function(element, callback) {
        var ids;
        ids = ($(element)).val();
        if (ids.indexOf('[') > -1 || ids.indexOf(']') > -1) {
          ids = ids.replace('[', '');
          ids = ids.replace(']', '');
          ($(element)).val(ids);
        }
        if (ids) {
          return $.getJSON("/contacts/ajax/?ids=" + ids, function(data) {
            return callback(data);
          });
        }
      },
      formatNoMatches: function(term) {
        if (term) {
          return "No se encontró \"" + term + "\" " + "<a href='/cases/add/contact' onclick='return showAddAnotherPopup(this);' class='add-another'>Agregar</a>";
        } else {
          return 'Entre un nombre';
        }
      },
      ajax: {
        url: '/contacts/ajax/',
        dataType: 'json',
        data: function(term, page) {
          return {
            q: term,
            page_limit: 20
          };
        },
        results: function(data, page) {
          return {
            results: data
          };
        }
      }
    });
    $('.request-button').click(function() {
      var codename;
      codename = $(this).attr('data-codename');
      $('#perm-codename').val(codename);
      return $('#request-modal').modal('show');
    });
    $doc = $(document);
    $mergeCaseContainer = $('.case-container');
    $event_list = $('#event-list');


    $doc.on('click', '.load-cases-button', function(event) {
      var $button, id, nextPage, oldText;
      $button = $(event.currentTarget);
      oldText = $button.text();
      $button.text('Cargando...');
      $button.attr('disabled', 'diabled');
     
      id = $button.data('case-id');
      nextPage = $button.data('case-next-page') || 1;


      return $.get("/cases/feed/?id=" + id, function(data) {

        //$mergeCaseContainer.append(data);

        $event_list.html(data)

        return $button.remove();
      }).fail(function(err) {
        
      });
    });
    $doc.on('click', '#caseFilter', function(event) {

      $div = $(event.currentTarget);
      id = $div.data('case-id');
      withEvents = $('#filterEvents').is(':checked')
      withNotes = $('#filterNotes').is(':checked')
      withMeetings = $('#filterMeetings').is(':checked')
      withImported = $('#filterImported').is(':checked')

      totalResult = $( "#totalResult option:selected" ).text();


      return $.get("/cases/feed/?id=" + id + "&with_events=" + withEvents + 
        "&with_notes=" + withNotes + "&with_meetings=" + withMeetings + "&with_imported=" + withImported + "&totalResult=" + totalResult, function(data) {

        //$mergeCaseContainer.append(data);

        $event_list.html(data)

        return;
      }).fail(function(err) {
        
      });

    })
    

    $inputText = $('.s3direct-upload');
    $form = $inputText.parents('form');
    inputName = $inputText.attr('name');
    className = $inputText.attr('class');
    if ($inputText.val() === '') {
      $inputText.after("<input type='file' name='" + inputName + "' class='" + className + "'>");
      $inputText.remove();
      $inputFilePicker = $('.s3direct-upload');
    } else {
      theValue = $inputText.val();
      $inputText.after("<input type='hidden' name='" + inputName + "' class='" + className + "' value='" + theValue + "'>");
      $inputText.after("<span class='s3direct-upload-progress'>" + theValue + "</span>");
      $inputText.remove();
      $inputFilePicker = $('.s3direct-upload');
    }
    return $inputFilePicker.on('change', function(event) {
      var s3upload;
      $('.btn.btn-grey').addClass('disabled');
      return s3upload = new S3Upload({
        file_dom_selector: '.s3direct-upload',
        s3_sign_put_url: '/cases/ajax/s3signature/',
        onProgress: function(percent, status, public_url, file) {
          var $progressLabel;
          $form.on('submit', function(event) {
            return event.preventDefault();
          });
          $progressLabel = $('.s3direct-upload-progress');
          $inputFilePicker.hide();
          if ($progressLabel.length > 0) {
            return $progressLabel.replaceWith("<span class='s3direct-upload-progress'>" + percent + "% Subiendo archivo...</span>");
          } else {
            return $inputFilePicker.after("<span class='s3direct-upload-progress'>" + percent + "% Subiendo archivo...</span>");
          }
        },
        onFinishS3Put: function(public_url, file, objectName) {
          var name;
          $form.off('submit');
          $('.s3direct-upload-progress').text("Completado: " + file.name);
          name = $inputFilePicker.attr('name');
          $inputFilePicker.after("<input type='hidden' name='" + name + "' value='" + objectName + "'>");
          $inputFilePicker.remove();
          return $('.btn.btn-grey').removeClass('disabled');
        },
        onError: function(status, file) {
          $('.s3direct-upload-progress').text("Error, trate de nuevo: " + status);
          return $inputFilePicker.show().val('');
        }
      });
    });
  };

  return AppView;

})(View);

});

require.alias("brunch/node_modules/deppack/node_modules/node-browser-modules/node_modules/buffer/index.js", "buffer");require.register("___globals___", function(exports, require, module) {
  
});})();require('___globals___');


//# sourceMappingURL=app.js.map
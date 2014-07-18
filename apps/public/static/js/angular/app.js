(function(){

  var app = angular.module('marketplace', [
                                           'ngRoute',
                                           'cloudinary',
                                           'market-directives',
                                           'market-controllers'
                                          ]);

  app.config(['$routeProvider',
    function($routeProvider) {
      $routeProvider.
        when('/product/:listingId', {
          templateUrl: 'partials/listing.html',
          controller: 'ListingController'
        }).
        otherwise({
          redirectTo: '/'
        });
    }
  ]);

})();

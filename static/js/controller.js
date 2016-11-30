/*global angular
global io
global location*/

var App = angular.module('D&DApp', []);


App.controller('Chat', function($scope) {
    var socket = io.connect('https://' + document.domain + ':' + location.port + '/Chat');
    $scope.messages = [];
    $scope.message = '';
    
    $scope.send = function send() {
        var temp = $scope.message;
        $scope.message = '';
        console.log(temp);
        socket.emit('write', temp);
    };

    socket.on('message', function(msg) {
        if (! ($scope.messages.indexOf(msg) > -1)){
        $scope.messages.push(msg);
        $scope.$apply();
        var elem = document.getElementById('msgpane');
        elem.scrollTop = elem.scrollHeight;
        }
    });
    
});
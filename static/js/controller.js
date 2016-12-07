/*global angular
global io
global location*/

var App = angular.module('D&DApp', []);


App.controller('Chat', function($scope) {
    var socket = io.connect('https://' + document.domain + ':' + location.port + '/Chat');
    $scope.messages = [];
    $scope.message = '';
    $scope.fill = '';
    $scope.fillIndex = $scope.messages.length;
    $scope.user = {};
    $scope.char = '';
    $scope.is_dm = true;
    
    // allows for keyup behavior like you see in terminals
    // $scope.keyup = function keyup($event) {
    //     if ($event.keyCode === 40) {
    //         if ($scope.fillIndex < $scope.messages.length) {
    //             do {
    //             $scope.fillIndex++;
    //             } while($scope.messages[$scope.fillIndex].character != $scope.user.character);

    //             $scope.fill = $scope.messages[$scope.fillIndex].body;
    //         }
    //         else {
    //             $scope.fill = '';
    //         }
    //     }
    //     else if ($scope.fillIndex > -1 && $event.keyCode === 38) {
    //         $scope.fillIndex--;
    //         $scope.fill = $scope.messages[$scope.fillIndex].body;
    //     }
    //     $scope.$apply();
    // };
    
    // emits messages to server
    $scope.send = function send() {
        var temp = $scope.message;
        $scope.message = '';
        socket.emit('write', temp);
    };

    // recieves messages from server
    socket.on('message', function(msg) {
        $scope.messages.push(msg);
        $scope.fillIndex = $scope.messages.length;
        $scope.$apply();
        var elem = document.getElementById('msgpane');
        elem.scrollTop = elem.scrollHeight;
    });
    
    socket.on('user', function(user) {
       $scope.user = user;
       $scope.char = user.character;
       if (user.is_dm == "0") {
           $scope.is_dm = false;
       }
       $scope.$apply();
       console.log($scope.user);
    });
    
});
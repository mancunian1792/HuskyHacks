'use strict';

module.exports = function(User) {

    User.remoteMethod (
        'authenticateNuser',
        {
            http: {path: '/authenticate', verb: 'post'},
            accepts: {arg: 'authObj', type: 'object', required: true, http: { source: 'body' }},
            returns: {root: true, type: 'object'},
            description: 'Marks a blog as upvoted.'
          
        }
    );

    User.authenticateNuser = function(authObj, cb) {
        console.log("Am i here??")
        console.log(JSON.stringify(authObj))
        User.findOne({
            where: {
                username: authObj.name,
                password: authObj.password
            }
        }, (err, resp) => {
            if (err) {
                return cb(err)
            }
            if(!resp) {
                var err = new Error("Username password don't match");
                err.statusCode = 403;
                return cb(err)
            }
            return cb(null, resp)
        })
    }

};

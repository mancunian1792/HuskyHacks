var dataSource = require(process.cwd() + "/server/server.js").dataSources["nuhub1"];
dataSource.automigrate(function(err) {
  if(err) {
    console.log("err in autoupdate:: ", err);
  }
  console.log("Success Bhen = automigrate")
  process.exit();
});
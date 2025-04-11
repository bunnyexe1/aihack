const linkedIn = require('linkedin-jobs-api');
const fs = require('fs');
const fetchJobsWithRetry = async (options, retries = 3, timeout = 30000) => {
  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      const response = await linkedIn.query(options, { timeout });
      return response;
    } catch (error) {
      if (attempt === retries) throw new Error("Failed to fetch jobs after multiple attempts.");
      await new Promise(res => setTimeout(res, attempt * 2000));
    }
  }
};

(async () => {
  try {
    const queryOptions = require('./query_options.json');
    const jobs = await fetchJobsWithRetry(queryOptions);
    
    // Print the JSON response in pretty format (with indentation for better readability)
   // const data = JSON.stringify(jobs, null, 2); // The '2' means 2 spaces for indentation
    fs.writeFileSync('jobs_data.json', JSON.stringify(jobs, null, 2), 'utf-8');
    //console.log(data);
   
  } catch (error) {
    // Print errors as JSON
    console.error(JSON.stringify({ error: error.message }, null, 2));
  }
})();
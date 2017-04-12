import { normalize, schema } from 'normalizr';
import 'isomorphic-fetch';


function addGetParams(url, params) {
  if (params) {
    const esc = encodeURIComponent;
    const query = Object.keys(params)
        .map(k => esc(k) + '=' + esc(params[k]))
        .join('&');
    return `${url}?${query}`;
  }
  return url;
}


const API_ROOT = '/api/v1/';

// Fetches an API response and normalizes the result JSON according to schema.
// This makes every API response have the same shape, regardless of how nested it was.
function callApi(endpoint, method, schema = null, getParams = null, postData = null) {
  const fullUrl = addGetParams(API_ROOT + endpoint, getParams);

  const myHeaders = new Headers({
    'Authorization': `Token ${localStorage.token}`,
    'Content-Type': 'application/json',
  });

  const myInit = {
    method: method,
    headers: myHeaders,
  };

  if (method === 'POST' || method === 'PUT') {
    myInit['body'] = JSON.stringify(postData);
  }

  return fetch(fullUrl, myInit)
      .then(response => {
        return response.text().then(text => {
          return { json: text ? JSON.parse(text) : {}, response };
        })
      })
      .then(({ json, response }) => {
        if (!response.ok) {
          return Promise.reject({error: json, response});
        }

        if (schema) {
          let data = json;
          let pagination = {};
          if (json.results) {
            data = json.results;
            pagination.count = json.count;
            pagination.page = 1;
            if (getParams && getParams.page) {
              pagination.page = getParams.page;
            }
          }
          console.log('response data -- ', json);
          console.log('response pagination -- ', pagination);
          return Object.assign(
              {},
              normalize(data, schema),
              { pagination },
          )
        }
        return json;
      })
      .then(
          response => ({response}),
          ({error, response}) => {
            let msg;
            if (error.detail) {
              msg = error.detail;
            } else if (error.non_field_errors) {
              msg = error.non_field_errors.join(' ');
            } else {
              msg = 'Something bad happened';
            }
            return {error: msg, status: response.status};
          }
      )

}

function getApi(endpoint, schema, getParams = null) {
  return callApi(endpoint, 'GET', schema, getParams);
}

function postApi(endpoint, schema, data) {
  return callApi(endpoint, 'POST', schema, null, data);
}

function putApi(endpoint, schema, data) {
  return callApi(endpoint, 'PUT', schema, null, data);
}

function deleteApi(endpoint) {
  return callApi(endpoint, 'DELETE');
}


const userSchema = new schema.Entity(
    'users',
    {},
    {
      idAttribute: 'username',
    },
);
const userSchemaArray = new schema.Array(userSchema);

const boxProviderSchema = new schema.Entity(
    'boxProviders',
    {},
    {
      idAttribute: 'tag',
    },
);
const boxProviderSchemaArray = new schema.Array(boxProviderSchema);

const boxVersionSchema = new schema.Entity(
    'boxVersions',
    {
      providers: boxProviderSchemaArray,
    },
    {
      idAttribute: 'tag',
    },
);
const boxVersionSchemaArray = new schema.Array(boxVersionSchema);

const boxSchema = new schema.Entity(
    'boxes',
    {
      versions: boxVersionSchemaArray,
    },
    {
      idAttribute: 'tag',
    },
);
const boxSchemaArray = new schema.Array(boxSchema);


export const fetchUser = ({ username }) => getApi(`users/${username}/`, userSchema);
export const fetchUsers = () => getApi('users/', userSchemaArray);

export const fetchBox = ({ tag }) => getApi(`boxes/${tag}/`, boxSchema);
export const fetchBoxes = ({ username, page, ordering }) => {
  let url = 'boxes/';
  if (username) {
    url = `boxes/${username}/`;
  }

  return getApi(
      url,
      boxSchemaArray,
      {
        page: page || 1,
        ordering: ordering || '-pulls',
      }
  );
};

export const fetchBoxVersion = ({ tag, version }) => getApi(
    `boxes/${tag}/versions/${version}/`,
    boxVersionSchema
);
export const fetchBoxVersions = ({ tag, page }) => {
  return getApi(
      `boxes/${tag}/versions/`,
      boxVersionSchemaArray,
      {page: page || 1}
  );
};

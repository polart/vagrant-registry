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
    'Content-Type': 'application/json',
  });

  if (localStorage.token) {
    myHeaders.set('Authorization', `Token ${localStorage.token}`);
  }

  const myInit = {
    method: method,
    headers: myHeaders,
  };

  if (method === 'POST' || method === 'PATCH') {
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
            return {error, status: response.status};
          }
      )

}

function getApi(endpoint, schema, getParams = null) {
  return callApi(endpoint, 'GET', schema, getParams);
}

// eslint-disable-next-line no-unused-vars
function postApi(endpoint, schema, data) {
  return callApi(endpoint, 'POST', schema, null, data);
}

// eslint-disable-next-line no-unused-vars
function patchApi(endpoint, schema, data) {
  return callApi(endpoint, 'PATCH', schema, null, data);
}

// eslint-disable-next-line no-unused-vars
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
export const fetchBoxes = ({ username, page, ordering, search }) => {
  let url = 'boxes/';
  if (username) {
    url = `boxes/${username}/`;
  }

  const query = {
    page: page || 1,
    ordering: ordering || '-pulls',
  };
  if (search) {
    query.search = search;
  }

  return getApi(
      url,
      boxSchemaArray,
      query,
  );
};
export const createBox = ({data, username}) => postApi(`boxes/${username}/`, boxSchema, data);
export const editBox = ({data, tag}) => patchApi(`boxes/${tag}/`, boxSchema, data);
export const deleteBox = ({tag}) => deleteApi(`boxes/${tag}/`);

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
export const createBoxVersion = ({data, tag}) => postApi(
    `boxes/${tag}/versions/`,
    boxVersionSchema,
    data
);
export const editBoxVersion = ({data, tag, version}) => patchApi(
    `boxes/${tag}/versions/${version}/`,
    boxVersionSchema,
    data
);
export const deleteBoxVersion = ({tag, version}) => deleteApi(
    `boxes/${tag}/versions/${version}/`
);

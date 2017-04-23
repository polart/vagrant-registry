export function getBoxTag(props) {
  const {username, boxName} = props.router.params;
  return `${username}/${boxName}`;
}

export function getBox(state, props) {
  return state.entities.boxes[ getBoxTag(props) ];
}

export function getBoxes(state, props, username = '__all__') {
  const boxPages = state.pagination.boxes[username];
  const queryPage = parseInt(props.router.location.query.page || 1, 10);
  const tags = (boxPages && boxPages.pages[queryPage]) || [];
  return {
    boxes: tags.map(tag => state.entities.boxes[tag]),
    totalCount: boxPages ? boxPages.count : 0,
  };
}

export function getBoxVersionTag(props) {
  const {username, boxName, version} = props.router.params;
  return `${username}/${boxName} v${version}`;
}

export function getBoxVersion(state, props) {
  return state.entities.boxVersions[ getBoxVersionTag(props) ];
}

export function getBoxProviderTag(props) {
  const {username, boxName, version, provider} = props.router.params;
  return `${username}/${boxName} v${version} ${provider}`;
}

export function getBoxProvider(state, props) {
  return state.entities.boxProviders[ getBoxProviderTag(props) ];
}

export function getBoxProviders(state, props) {
  const version = getBoxVersion(state, props);
  if (version && version.providers) {
    return version.providers.map(
      tag => state.entities.boxProviders[tag]
    );
  }
  return [];
}

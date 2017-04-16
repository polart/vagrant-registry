export const parsePerms = (permissions) => {
  if (permissions === '*') {
    return {
      canPull: true,
      canPush: true,
      canEdit: true,
      canDelete: true,
    }
  } else if (permissions === 'RW') {
    return {
      canPull: true,
      canPush: true,
      canEdit: false,
      canDelete: false,
    }
  } else if (permissions === 'R') {
    return {
      canPull: true,
      canPush: false,
      canEdit: false,
      canDelete: false,
    }
  }
  return {
    canPull: false,
    canPush: false,
    canEdit: false,
    canDelete: false,
  }
};

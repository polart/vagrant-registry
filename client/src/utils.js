import SparkMD5 from 'spark-md5';

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

export const getFileMD5Hash = (file) => {
  return new Promise((resolve) => {
    const blobSlice = File.prototype.slice || File.prototype.mozSlice || File.prototype.webkitSlice;
    const chunkSize = 2097152;  // Read in chunks of 2MB
    const chunks = Math.ceil(file.size / chunkSize);
    const spark = new SparkMD5.ArrayBuffer();
    const fileReader = new FileReader();
    let currentChunk = 0;

    fileReader.onload = function (e) {
      spark.append(e.target.result);  // Append array buffer
      currentChunk += 1;

      if (currentChunk < chunks) {
        loadNextChunk();
      } else {
        // Returning hex hash
        resolve(spark.end(false));
      }
    };

    function loadNextChunk() {
      const start = currentChunk * chunkSize;
      const end = ((start + chunkSize) >= file.size) ? file.size : start + chunkSize;

      fileReader.readAsArrayBuffer(blobSlice.call(file, start, end));
    }

    loadNextChunk();
  });
};

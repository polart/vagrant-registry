import React, {Component} from "react";
import {connect} from "react-redux";
import {isArray} from "lodash";
import * as actions from "../actions";
import {ControlLabel, FormGroup, HelpBlock, ProgressBar} from "react-bootstrap";
import Filesize from "filesize";


class BoxFileFormField extends Component {
  state = {
    file: null,
    fileLabelText: 'Choose file',
  };

  onChange = (e) => {
    this.props.updateFormData('boxProvider', {
      progress: null,
      status: null,
    });
    if (!e.target.files.length) {
      this.setState({
        file: null,
        fileLabelText: 'Choose file',
      });
      this.props.onChange(null);
      return;
    }

    const file = e.target.files[0];
    this.setState({
      file,
      fileLabelText: `${file.name} (${Filesize(file.size)})`,
    });

    this.props.onChange(file);
  };

  renderErrors = () => {
    if (!this.props.errors) {
      return null;
    }
    let errors = this.props.errors;
    if (!isArray(errors)) {
      errors = [errors];
    }
    return errors.map((error, index) => {
      return <HelpBlock key={index}>{error}</HelpBlock>;
    });
  };

  renderUploadStatus = () => {
    if (this.props.formData.uploadStatus) {
      return <HelpBlock>{this.props.formData.uploadStatus}</HelpBlock>
    }
    return null;
  };

  renderUploadProgress = () => {
    if (this.props.formData.uploadProgress) {
      const progress = this.props.formData.uploadProgress;
      const perc = progress.loaded / progress.totalSize * 100;
      return <ProgressBar
          now={perc}
          bsStyle={perc === 100 ? 'success' : null}
          label={`${perc.toFixed(0)}% (${Filesize(progress.loaded)})`}
      />;
    }
    return null;
  };

  getValidationState = () => {
    if (this.props.errors) {
      return 'error';
    }
    return null;
  };

  render() {

    return (
        <FormGroup
            controlId={this.props.model}
            validationState={this.getValidationState()}
        >
          <ControlLabel>{this.props.label}</ControlLabel>
          <input
              id="boxFile"
              type="file"
              ref="boxFile"
              style={{visibility: 'hidden', height: 0, width: 0}}
              accept=".box"
              onChange={this.onChange}
          />
          <label htmlFor="boxFile" className="btn btn-default">{this.state.fileLabelText}</label>
          {this.renderUploadStatus()}
          {this.renderUploadProgress()}
          {this.renderErrors()}
        </FormGroup>
    );
  }
}

function mapStateToProps(state, props) {
  const modelPath = props.model.split('.');
  const form = state.forms[modelPath[0]];
  return {
    formData: form.data,
    errors: form.errors[modelPath[1]],
  }
}

export default connect(mapStateToProps, {
  updateFormData: actions.form.updateData,
})(BoxFileFormField)

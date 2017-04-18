import React, {Component} from "react";
import {Button} from "react-bootstrap";
import MyFormField from "./MyFormField";
import MyFormError from "./MyFormError";
import MySubmitButton from "./MySubmitButton";
import BoxFileFormField from "./BoxFileFormField";


class BoxProviderForm extends Component {
  render() {
    return (
        <form onSubmit={this.props.onSubmit}>
          <MyFormError model="boxProvider" />
          <MyFormField
              model='boxProvider.provider'
              type='text'
              label='Provider *'
          />
          <BoxFileFormField
              model='boxProvider.file'
              label='Box file'
              onChange={this.props.onFileInputChange}
          />

          <MySubmitButton
              title={this.props.submitTitle}
              pendingTitle={this.props.submitPendingTitle}
              pending={this.props.pending}
          />
          {' '}
          <Button
              bsStyle="link"
              onClick={this.props.onCancel}
          >
            Cancel
          </Button>
        </form>
    );
  }
}

export default BoxProviderForm;

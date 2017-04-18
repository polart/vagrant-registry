import React, {Component} from "react";
import {connect} from "react-redux";
import {PageHeader} from "react-bootstrap";
import * as actions from "../actions";
import BoxForm from "./BoxForm";
import {isEqual} from "lodash";


class BoxEditPage extends Component {
  componentDidMount() {
    if (!this.props.myUsername) {
      this.props.router.push(`/login/?next=${location.pathname}`);
      return;
    }
    if (!this.props.box) {
      this.props.loadBox(this.props.tag);
      return;
    }
    this.props.setFormData('box', this.props.box);
  }

  componentDidUpdate(prevProps) {
    if (!isEqual(prevProps.box, this.props.box)) {
      // For a case when box data loaded
      this.props.setFormData('box', this.props.box);
    }
  }

  onSubmit = (e) => {
    e.preventDefault();
    this.props.editBox(this.props.tag, this.props.form.data);
  };

  onCancel = () => {
      this.props.router.push(`/boxes/${this.props.tag}/`);
  };

  render() {
    return (
        <div>
          <PageHeader>Edit box</PageHeader>
          <BoxForm
              pending={this.props.form.pending}
              submitTitle='Save'
              submitPendingTitle="Saving..."
              onSubmit={this.onSubmit}
              onCancel={this.onCancel}
          />
        </div>
    );
  }
}

function mapStateToProps(state, props) {
  const {username, boxName} = props.router.params;
  const tag = `${username}/${boxName}`;
  const box = state.entities.boxes[tag];
  return {
    myUsername: state.myUsername,
    form: state.forms.box,
    tag,
    box,
  }
}

export default connect(mapStateToProps, {
  loadBox: actions.loadBox,
  editBox: actions.editBox,
  setFormData: actions.form.setData,
})(BoxEditPage)

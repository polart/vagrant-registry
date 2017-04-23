import React, {Component} from "react";
import {connect} from "react-redux";
import {Panel} from "react-bootstrap";
import * as actions from "../actions";
import BoxForm from "./BoxForm";
import {isEqual} from "lodash";
import BoxPageHeader from "./BoxPageHeader";
import MyBreadcrumbs from "./MyBreadcrumbs";
import {getBox, getBoxTag} from "../selectors";


class BoxEditPage extends Component {
  componentDidMount() {
    if (!this.props.myUsername) {
      this.props.router.push(`/login/?next=${location.pathname}`);
      return;
    }
    if (!this.props.box) {
      this.props.loadBox(this.props.boxTag);
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

  componentWillUnmount() {
    this.props.resetForm('box');
  }

  onSubmit = (e) => {
    e.preventDefault();
    this.props.editBox(this.props.boxTag, this.props.form.data);
  };

  onCancel = () => {
    this.props.router.push(`/boxes/${this.props.boxTag}/`);
  };

  render() {
    return (
        <div>
          <BoxPageHeader router={this.props.router} />
          <MyBreadcrumbs router={this.props.router} />
          <Panel header="Edit box">
            <BoxForm
                pending={this.props.form.pending}
                submitTitle='Save'
                submitPendingTitle="Saving..."
                onSubmit={this.onSubmit}
                onCancel={this.onCancel}
            />
          </Panel>
        </div>
    );
  }
}

function mapStateToProps(state, props) {
  return {
    myUsername: state.myUsername,
    form: state.forms.box,
    box: getBox(state, props),
    boxTag: getBoxTag(props),
  }
}

export default connect(mapStateToProps, {
  loadBox: actions.loadBox,
  editBox: actions.editBox,
  setFormData: actions.form.setData,
  resetForm: actions.form.reset,
})(BoxEditPage)

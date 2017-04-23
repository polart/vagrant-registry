import React, {Component} from "react";
import {connect} from "react-redux";
import {Panel} from "react-bootstrap";
import * as actions from "../actions";
import MyBreadcrumbs from "./MyBreadcrumbs";
import BoxVersionForm from "./BoxVersionForm";
import BoxPageHeader from "./BoxPageHeader";
import {getBoxTag} from "../selectors";


class BoxVersionCreatePage extends Component {
  componentDidMount() {
    if (!this.props.myUsername) {
      this.props.router.push(`/login/?next=${location.pathname}`);
    }
  }

  componentWillUnmount() {
    this.props.resetForm('boxVersion');
  }

  onSubmit = (e) => {
    e.preventDefault();
    this.props.createBoxVersion(this.props.boxTag, this.props.form.data);
  };

  onCancel = () => {
    this.props.router.push(
        `/boxes/${this.props.boxTag}/versions/`
    );
  };

  render() {
    return (
        <div>
          <BoxPageHeader router={this.props.router} />
          <MyBreadcrumbs router={this.props.router} />
          <Panel header="New version">
            <BoxVersionForm
                pending={this.props.form.pending}
                submitTitle='Create'
                submitPendingTitle="Creating..."
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
    form: state.forms.boxVersion,
    boxTag: getBoxTag(props),
  }
}

export default connect(mapStateToProps, {
  createBoxVersion: actions.createBoxVersion,
  resetForm: actions.form.reset,
})(BoxVersionCreatePage)

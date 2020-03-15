import React, {Component} from "react";
import {connect} from "react-redux";
import {merge} from "lodash";
import * as actions from "../actions";
import MyBreadcrumbs from "./MyBreadcrumbs";
import BoxProviderForm from "./BoxProviderForm";
import BoxVersionPageHeader from "./BoxVersionPageHeader";
import {Panel} from "react-bootstrap";
import {getBoxTag} from "../selectors";


class BoxProviderCreatePage extends Component {
  state = {
    file: null,
  };

  componentDidMount() {
    if (!this.props.myUsername) {
      this.props.router.push(`/login/?next=${window.location.pathname}`);
    }
  }

  componentWillUnmount() {
    this.props.resetForm('boxProvider');
  }

  onSubmit = (e) => {
    e.preventDefault();
    this.props.createBoxProvider(
        this.props.boxTag,
        this.props.params.version,
        merge({}, this.props.form.data, {file: this.state.file})
    );
  };

  onFileInputChange = (file) => {
    this.setState({ file });
  };

  onCancel = () => {
    this.props.router.push(
        `/boxes/${this.props.boxTag}/versions/${this.props.params.version}/`
    );
  };

  render() {
    return (
        <div>
          <BoxVersionPageHeader router={this.props.router} />
          <MyBreadcrumbs router={this.props.router} />
          <Panel header="New provider">
            <BoxProviderForm
                pending={this.props.form.pending}
                submitTitle='Create'
                submitPendingTitle="Creating..."
                onSubmit={this.onSubmit}
                onCancel={this.onCancel}
                onFileInputChange={this.onFileInputChange}
            />
          </Panel>
        </div>
    );
  }
}

function mapStateToProps(state, props) {
  return {
    myUsername: state.myUsername,
    form: state.forms.boxProvider,
    boxTag: getBoxTag(props),
  }
}

export default connect(mapStateToProps, {
  createBoxProvider: actions.createBoxProvider,
  resetForm: actions.form.reset,
})(BoxProviderCreatePage)

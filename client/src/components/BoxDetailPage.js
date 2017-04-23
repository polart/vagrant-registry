import React, {Component} from "react";
import {connect} from "react-redux";
import {Panel, Tab, Tabs} from "react-bootstrap";
import ReactMarkdown from "react-markdown";
import * as actions from "../actions";
import BoxVersionList from "./BoxVersionList";
import MyBreadcrumbs from "./MyBreadcrumbs";
import {Link} from "react-router";
import {parsePerms} from "../utils";
import MySpinner from "./MySpinner";
import BoxPageHeader from "./BoxPageHeader";
import {getBox, getBoxTag} from "../selectors";

import '../styles/BoxDetailPage.css';


class BoxDetailPage extends Component {
  componentDidMount() {
    this.props.fetchBox(this.props.boxTag);
  }

  onTabSelect = (eventKey) => {
    if (eventKey === 'info') {
      this.props.router.push(`/boxes/${this.props.boxTag}/`);
    } else if (eventKey === 'versions') {
      this.props.router.push(`/boxes/${this.props.boxTag}/versions/`);
    }
  };

  renderBoxDetails = () => {
    if (!this.props.box) {
      return <MySpinner />;
    }

    return (
      <div>
        <Panel header="Quick start" className="box-quick-start-panel">
          <pre>
            <p>vagrant init {this.props.boxTag} {window.location.origin}/{this.props.boxTag}</p>
            <p>vagrant up</p>
          </pre>
        </Panel>
        {!!this.props.box.short_description.length &&
          <Panel header="Short description">
            {this.props.box.short_description}
          </Panel>
        }
        {!!this.props.box.description.length &&
          <Panel header="Description">
            <ReactMarkdown source={this.props.box.description} />
          </Panel>
        }
      </div>
    );
  };

  renderNewVersionButton = () => {
    if (!this.props.box) {
      return null;
    }
    if (parsePerms(this.props.box.user_permissions).canPush) {
      return (
          <Link to={`/boxes/${this.props.boxTag}/versions/new/`}
                className='btn btn-success box-version-new-button'>
          New version
          </Link>
      );
    }
    return null;
  };

  render() {
    const activeTab = this.props.location.pathname.endsWith('/versions/') ? 'versions' : 'info';
    return (
        <div>
          <BoxPageHeader router={this.props.router} />
          <MyBreadcrumbs router={this.props.router} />
          <Tabs
              id="box-tabs"
              defaultActiveKey={activeTab}
              onSelect={this.onTabSelect}
          >
            <Tab eventKey={'info'} title="Box Info">
              {this.renderBoxDetails()}
            </Tab>
            <Tab eventKey={'versions'} title="Versions">
              {this.renderNewVersionButton()}
              <BoxVersionList boxTag={this.props.boxTag} />
            </Tab>
          </Tabs>
        </div>
    );
  }
}

function mapStateToProps(state, props) {
  return {
    box: getBox(state, props),
    boxTag: getBoxTag(props),
  }
}

export default connect(mapStateToProps, {
  fetchBox: actions.loadBox,
  deleteBox: actions.deleteBox,
})(BoxDetailPage)
